"""Media service for handling file uploads and media management"""

from typing import List

from app.modules.posts.schema.post import PostMediaItem


class MediaService:
    """Service for media file management"""

    async def upload_post_media(self, file, user_id: str) -> str:
        """Upload post media file and return URL"""
        raise NotImplementedError("Media upload not implemented yet")

    async def add_media_items_to_post(
        self, session, post_id: str, media_items: List[PostMediaItem]
    ) -> None:
        """Add media items to a post"""
        raise NotImplementedError("Media items management not implemented yet")


# Create singleton instance
media_service = MediaService()
