from models.blogs import Blog
from api.routers.blogs import get_blogs

class FakeQuery:
    def __init__(self, data):
        self._data = data
    def filter(self, *args, **kwargs):
        # ignoring filter expression, assume data is already filtered
        return self
    def all(self):
        return self._data

class FakeDB:
    def __init__(self, data):
        self._data = data
    def query(self, model):
        return FakeQuery(self._data)


def make_blog(id, title, content, active=True):
    b = Blog()
    # Blog columns are simple attributes; set them directly
    b.id = str(id)
    b.title = title
    b.content = content
    b.images = []
    b.videos = []
    b.tags = []
    b.links = []
    b.active = active
    from datetime import datetime
    b.created_at = datetime.utcnow()
    b.updated_at = datetime.utcnow()
    return b


def run_test():
    blogs = [
        make_blog('1', 'First blog', 'Content 1', active=True),
        make_blog('2', 'Second blog', 'Content 2', active=False),
        make_blog('3', 'Third blog', 'Content 3', active=True),
    ]
    # Only active ones should be returned by get_blogs
    fake_db = FakeDB([b for b in blogs if b.active])
    result = get_blogs(db=fake_db)
    print('GET /blogs returned:')
    for r in result:
        print('-', r.id, r.title, 'active=', r.active)

if __name__ == '__main__':
    run_test()
