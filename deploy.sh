#!/bin/bash
set -e

#!/bin/bash
set -e

# ════════════════════════════════════════════════
# ║       NEWS PORTAL DEPLOYMENT SCRIPT          ║
# ════════════════════════════════════════════════

# Default branch to deploy
DEPLOY_BRANCH="${1:-main}"
FORCE_CLEAN="${2:-false}"

# Show usage if help is requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: $0 [branch_name] [force]"
  echo "  branch_name: Branch to deploy (default: main)"
  echo "  force: Set to 'force' for complete clean deployment"
  echo ""
  echo "Examples:"
  echo "  $0              # Deploy main branch"
  echo "  $0 main         # Deploy main branch"
  echo "  $0 main force   # Deploy main with complete Docker cleanup"
  echo "  $0 develop      # Deploy develop branch"
  exit 0
fi

# Determine Docker image tag based on branch
if [[ "$DEPLOY_BRANCH" == "main" ]]; then
  DOCKER_TAG="ghcr.io/bibektimilsina00/news-portal:deploy"
elif [[ "$DEPLOY_BRANCH" == "develop" ]]; then
  DOCKER_TAG="ghcr.io/bibektimilsina00/news-portal:develop-deploy"
else
  # For feature branches, use branch-specific tag
  BRANCH_TAG=$(echo "$DEPLOY_BRANCH" | sed 's/[^a-zA-Z0-9]/-/g')
  DOCKER_TAG="ghcr.io/bibektimilsina00/news-portal:${BRANCH_TAG}-deploy"
fi

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log_header() {
  echo -e "\n${BOLD}${BLUE}═════════════════════════════════════════════════${NC}"
  echo -e "${BOLD}${BLUE}   ${1}${NC}"
  echo -e "${BOLD}${BLUE}═════════════════════════════════════════════════${NC}\n"
}

log_info() {
  echo -e "${CYAN}[$(date "+%H:%M:%S")]${NC} ${1}"
}

log_success() {
  echo -e "${GREEN}[$(date "+%H:%M:%S")]${NC} ✅ ${GREEN}${1}${NC}"
}

log_warning() {
  echo -e "${YELLOW}[$(date "+%H:%M:%S")]${NC} ⚠️  ${YELLOW}${1}${NC}"
}

log_error() {
  echo -e "${RED}[$(date "+%H:%M:%S")]${NC} ❌ ${RED}${1}${NC}"
}

log_step() {
  echo -e "${PURPLE}[$(date "+%H:%M:%S")]${NC} 🔹 ${1}"
}

log_progress_start() {
  echo -en "${CYAN}[$(date "+%H:%M:%S")]${NC} ⏳ ${1} "
}

log_progress_done() {
  echo -e "${GREEN}${1}${NC}"
}

# Function to handle special environment variables
handle_env_var() {
  local line="$1"
  local key="${line%%=*}"
  local value="${line#*=}"
  
  # For BACKEND_CORS_ORIGINS, just export it as is
  if [ "$key" == "BACKEND_CORS_ORIGINS" ]; then
    export "$key=$value"
    return
  fi
  
  export "$key=$value"
}

# Load environment variables
log_header "INITIALIZING DEPLOYMENT"

log_info "Deployment branch: ${BOLD}${DEPLOY_BRANCH}${NC}"
log_info "Docker image: ${BOLD}${DOCKER_TAG}${NC}"

# Git repository update and branch switching
log_step "Updating repository and switching to $DEPLOY_BRANCH branch..."
if [ -d ".git" ]; then
  # Fetch latest changes
  git fetch origin > /dev/null 2>&1 || log_warning "Failed to fetch from origin"
  
  # Check current branch
  CURRENT_BRANCH=$(git branch --show-current)
  log_info "Current branch: $CURRENT_BRANCH"
  
  # Switch to target branch
  if [ "$CURRENT_BRANCH" != "$DEPLOY_BRANCH" ]; then
    log_step "Switching from $CURRENT_BRANCH to $DEPLOY_BRANCH..."
    git checkout "$DEPLOY_BRANCH" > /dev/null 2>&1 || {
      log_warning "Failed to checkout $DEPLOY_BRANCH branch, trying to create it..."
      git checkout -b "$DEPLOY_BRANCH" "origin/$DEPLOY_BRANCH" > /dev/null 2>&1 || {
        log_error "Failed to switch to $DEPLOY_BRANCH branch"
        exit 1
      }
    }
    log_success "Switched to $DEPLOY_BRANCH branch"
  else
    log_success "Already on $DEPLOY_BRANCH branch"
  fi
  
  # Pull latest changes from target branch
  git pull origin "$DEPLOY_BRANCH" > /dev/null 2>&1 || log_warning "Failed to pull latest changes"
  
  # Show current commit
  CURRENT_COMMIT=$(git rev-parse --short HEAD)
  COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "Unknown")
  log_success "Repository updated to commit: $CURRENT_COMMIT"
  log_info "Latest commit: ${BOLD}${COMMIT_MESSAGE}${NC}"
else
  log_warning "Not a git repository - skipping branch switch"
fi

if [ -f ".backend.env" ]; then
  log_info "Loading environment variables..."
  
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]] && continue
    handle_env_var "$line"
  done < .backend.env
  log_success "Environment variables loaded successfully"
else
  log_error "No .env file found. Please create one."
  exit 1
fi

# Check required variables
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_DB" ]; then
  log_error "Missing required database environment variables."
  exit 1
fi

log_header "STARTING ZERO-DOWNTIME DEPLOYMENT"

# Create network and volumes if they don't exist
log_step "Creating Docker resources..."
docker network create app-network 2>/dev/null || true
docker volume create postgres_data 2>/dev/null || true
docker volume create static_files 2>/dev/null || true
docker volume create uv_cache 2>/dev/null || true
docker volume create venv_data 2>/dev/null || true
log_success "Docker resources ready"

# Pull images first before stopping anything
log_step "Pulling latest images..."
log_info "Forcing fresh pull of: ${BOLD}${DOCKER_TAG}${NC}"

# If force clean is requested, do aggressive cleanup first
if [ "$FORCE_CLEAN" = "force" ]; then
  log_warning "Force clean mode - removing all Docker cache and containers..."
  docker system prune -af 2>/dev/null || true
  docker volume prune -f 2>/dev/null || true
  log_success "Docker cleanup completed"
fi

# Force remove local image first to ensure fresh pull
docker rmi "$DOCKER_TAG" 2>/dev/null || log_info "No local image to remove"

# Pull with --pull=always equivalent behavior
docker pull postgres:16-alpine &> /dev/null &
PULL1_PID=$!
docker pull "$DOCKER_TAG" --quiet &
PULL2_PID=$!

# Show a spinner while pulling
CHARS="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
i=0
while kill -0 $PULL1_PID 2>/dev/null || kill -0 $PULL2_PID 2>/dev/null; do
  i=$(( (i+1) % ${#CHARS} ))
  echo -ne "\r${CYAN}[$(date "+%H:%M:%S")]${NC} 🔄 Pulling latest images... ${CHARS:$i:1} "
  sleep 0.2
done
echo -e "\r${CYAN}[$(date "+%H:%M:%S")]${NC} 🔄 Pulling latest images... ${GREEN}Done${NC}"

# Verify we got the latest image
log_step "Verifying image details..."
IMAGE_ID=$(docker images --format "{{.ID}}" "$DOCKER_TAG" | head -1)
IMAGE_CREATED=$(docker images --format "{{.CreatedAt}}" "$DOCKER_TAG" | head -1)
log_info "Image ID: ${BOLD}${IMAGE_ID}${NC}"
log_info "Image created: ${BOLD}${IMAGE_CREATED}${NC}"

# Start database if not running
log_header "DATABASE SETUP"
if ! docker ps | grep -q database; then
  log_step "Starting database container..."
  docker run -d \
    --name database \
    --restart unless-stopped \
    --network app-network \
    -p "${POSTGRES_PORT:-5432}:5432" \
    -v postgres_data:/var/lib/postgresql/data \
    -e POSTGRES_USER="$POSTGRES_USER" \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e POSTGRES_DB="$POSTGRES_DB" \
    --health-cmd="pg_isready -h localhost -p 5432 -U $POSTGRES_USER" \
    --health-interval=10s \
    --health-timeout=5s \
    --health-retries=5 \
    postgres:16-alpine > /dev/null
  log_success "Database container started"
else
  log_success "Database already running"
fi

# Wait for database to be healthy
log_progress_start "Waiting for database to be ready..."
i=0
until docker inspect --format "{{.State.Health.Status}}" database | grep -q "healthy"; do
  i=$(( (i+1) % ${#CHARS} ))
  echo -ne "${CHARS:$i:1} "
  sleep 0.2
done
log_progress_done "Database ready!"

# Blue-Green Deployment for Backend
log_header "BACKEND DEPLOYMENT (BLUE-GREEN)"

# Blue is always the temporary container, green is always production
# Remove blue container if it exists
if docker ps -a --filter "name=news-portal-blue" | grep -q "news-portal-blue"; then
  log_step "Removing existing blue container..."
  docker stop news-portal-blue 2>/dev/null || true
  docker rm news-portal-blue 2>/dev/null || true
  log_success "Blue container removed"
fi

# Start new blue container for testing
log_step "Starting temporary backend container (blue)..."
log_info "Using Docker image: ${BOLD}${DOCKER_TAG}${NC}"
CONTAINER_ID=$(docker run -d \
  --name news-portal-blue \
  --restart unless-stopped \
  --network app-network \
  -p "8081:8080" \
  -v uv_cache:/home/appuser/.cache/uv \
  -v venv_data:/app/.venv \
  --env-file .backend.env \
  "$DOCKER_TAG")
  
# Print shorter container ID
SHORT_ID=${CONTAINER_ID:0:12}
log_success "Blue container started (ID: ${SHORT_ID})"

# Check initial container status
log_step "Checking container logs (first 5 lines)..."
sleep 3
docker logs news-portal-blue --tail 5

# Wait for new container to be healthy
log_progress_start "Waiting for blue container to be ready..."
sleep 10
HEALTH_CHECK_URL="http://localhost:8081/health/"
RETRIES=0
MAX_RETRIES=50

until curl -s -f "$HEALTH_CHECK_URL" > /dev/null || [ $RETRIES -ge $MAX_RETRIES ]; do
  i=$(( (i+1) % ${#CHARS} ))
  echo -ne "${CHARS:$i:1} "
  sleep 1
  RETRIES=$((RETRIES + 1))
done

if [ $RETRIES -ge $MAX_RETRIES ]; then
  log_error "Blue container failed health check! Aborting deployment..."
  docker stop news-portal-blue 2>/dev/null || true
  docker rm news-portal-blue 2>/dev/null || true
  exit 1
fi

log_progress_done "Blue container is healthy!"

# If tests pass, deploy to production (green)
log_step "Deploying to production container (green)..."

# Stop and remove existing green container if it exists
if docker ps -a --filter "name=news-portal-green" | grep -q "news-portal-green"; then
  log_step "Stopping and removing current production container..."
  docker stop news-portal-green 2>/dev/null || true
  docker rm news-portal-green 2>/dev/null || true
  log_success "Old green container removed"
fi

# Wait a moment to ensure the port is freed
sleep 2

# Start new green container on production port
GREEN_ID=$(docker run -d \
  --name news-portal-green \
  --restart unless-stopped \
  --network app-network \
  -p "8080:8080" \
  -v uv_cache:/home/appuser/.cache/uv \
  -v venv_data:/app/.venv \
  --env-file .backend.env \
  "$DOCKER_TAG")

# Print shorter container ID  
SHORT_GREEN_ID=${GREEN_ID:0:12}
log_success "Green container deployed successfully (ID: ${SHORT_GREEN_ID})"

# Clean up blue container 
log_step "Cleaning up temporary blue container..."
docker stop news-portal-blue 2>/dev/null || true
docker rm news-portal-blue 2>/dev/null || true
log_success "Blue container cleaned up"

# Clean up outdated containers and images
log_step "Cleaning up outdated resources..."
docker container prune -f > /dev/null
docker image prune -f > /dev/null
log_success "Cleanup completed"

# Verify deployment
log_header "DEPLOYMENT SUMMARY"

echo -e "${BOLD}${CYAN}Container Status:${NC}"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${BOLD}${CYAN}Deployed Image Details:${NC}"
DEPLOYED_IMAGE_ID=$(docker inspect news-portal-green --format "{{.Image}}")
DEPLOYED_IMAGE_TAG=$(docker inspect news-portal-green --format "{{index .Config.Image}}")
echo -e "Image: ${BOLD}${DEPLOYED_IMAGE_TAG}${NC}"
echo -e "Image ID: ${BOLD}${DEPLOYED_IMAGE_ID:0:12}${NC}"

# Show environment and branch info from container
echo -e "\n${BOLD}${CYAN}Container Environment:${NC}"
docker exec news-portal-green env | grep -E "APP_ENV|GIT_BRANCH" 2>/dev/null || echo "Environment variables not available"

echo -e "\n${BOLD}${CYAN}Backend Logs:${NC}"
docker logs news-portal-green --tail 10

log_success "Zero-downtime deployment completed successfully!"
echo -e "\n${BOLD}${GREEN}✨ Backend is now running on port 8080 ✨${NC}\n"

# Final verification
if [ -d ".git" ]; then
  FINAL_COMMIT=$(git rev-parse --short HEAD)
  echo -e "${BOLD}${CYAN}Deployed from commit:${NC} ${BOLD}${FINAL_COMMIT}${NC}"
fi