from pathlib import Path
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.session import Base
from models.blogs import Blog
from dashboard.routers.blog import (
    list_blogs, add_blog, create_blog, view_blog, edit_blog, delete_blog
)
from types import SimpleNamespace
from datetime import datetime, timezone

# Setup in-memory SQLite DB for testing
engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Fake current user (Tenant-like)
class FakeUser:
    def __init__(self):
        self.email = 'admin@example.com'
        self.role = 'admin'
        self.id = 'admin-1'

# Minimal fake Request object with session and url_for
class FakeRequest:
    def __init__(self):
        self.session = {}
    def url_for(self, name):
        # Simulate URL for list_blogs
        if name == 'list_blogs':
            return '/admin/blogs'
        return '/'


import asyncio


async def run_tests():
    db = SessionLocal()
    user = FakeUser()
    req = FakeRequest()

    # 1) Test list_blogs when empty
    resp = await list_blogs(request=req, current_user=user, db=db)
    print('list_blogs returned TemplateResponse object:', type(resp))

    # 2) Test create_blog (POST)
    # Need CSRF setup
    req.session['csrf_token'] = 'token-123'
    # Call create_blog with form params
    redirect = await create_blog(
        request=req,
        title='Test Blog',
        content='This is a test blog',
        slug=None,
        status='published',
        tags='test,blog',
        links='http://example.com',
        images='[]',
        videos='[]',
        csrf_token='token-123',
        current_user=user,
        db=db
    )
    print('create_blog returned:', type(redirect))

    # Verify blog created in DB
    created = db.query(Blog).filter(Blog.title == 'Test Blog').first()
    print('Created blog found:', bool(created), 'id=', getattr(created, 'id', None))

    # 3) Test view_blog with numeric id: create a blog with id '123' to satisfy isdigit check
    b2 = Blog(id='123', title='Numeric Blog', content='Num content', images=[], videos=[], tags=[], links=[], active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db.add(b2)
    db.commit()

    try:
        view_resp = await view_blog(blog_id=123, request=req, current_user=user, db=db)
        print('view_blog returned TemplateResponse-like:', type(view_resp))
    except Exception as e:
        print('view_blog raised:', e)

    # 4) Test edit_blog (GET update form)
    try:
        edit_resp = await edit_blog(blog_id=123, request=req, current_user=user, db=db)
        print('edit_blog returned TemplateResponse-like:', type(edit_resp))
    except Exception as e:
        print('edit_blog raised:', e)

    # 5) Test delete_blog
    try:
        del_resp = await delete_blog(blog_id='123', request=req, current_user=user, db=db)
        print('delete_blog returned:', type(del_resp))
        # Check deletion
        gone = db.query(Blog).filter(Blog.id == '123').first()
        print('Blog deleted from DB:', gone is None)
    except Exception as e:
        print('delete_blog raised:', e)

    db.close()


if __name__ == '__main__':
    asyncio.run(run_tests())
