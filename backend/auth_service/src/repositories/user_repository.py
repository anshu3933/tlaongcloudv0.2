from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from ..models.user import User
from ..models.user_session import UserSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False

    async def list_all(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_user(self, user_id: UUID) -> Optional[Dict]:
        """Get user by ID and return as dictionary"""
        user = await self.get_by_id(user_id)
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "role": user.role
            }
        return None

    async def create_session(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.session.add(session)
        await self.session.commit()

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.update(user)

    async def get_users_by_role(self, role: str) -> List[Dict]:
        """Get all active users with a specific role"""
        result = await self.session.execute(
            select(User).where(
                and_(
                    User.role == role,
                    User.is_active == True
                )
            )
        )
        users = result.scalars().all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
            for user in users
        ]
