# import unittest
# from unittest.mock import AsyncMock, MagicMock
# from fastapi import HTTPException
# from photoshare.database.models import Tag
# from photoshare.repository.tags import create_tag, get_tag, remove_tag, update_tag

# class TestTagRepository(unittest.IsolatedAsyncioTestCase):

#     async def asyncSetUp(self):
#         self.db = MagicMock()
#         self.body = {"name": "test"}
#         self.tag = Tag(id=1, name='test')

#     async def test_create_tag(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = None
#         self.db.add = AsyncMock()
#         self.db.commit = AsyncMock()

#         await create_tag(body=self.body, db=self.db)
#         self.db.query.assert_called_once_with(Tag)
#         self.db.add.assert_called_once()
#         self.db.commit.assert_called_once()

#     async def test_create_tag_already_exists(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = self.tag

#         with self.assertRaises(HTTPException) as context:
#             await create_tag(body=self.body, db=self.db)
        
#         self.assertEqual(context.exception.status_code, 400)
#         self.db.query.assert_called_once_with(Tag)

#     async def test_get_tag(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = self.tag

#         result = await get_tag(tag_id=1, db=self.db)
#         self.db.query.assert_called_once_with(Tag)
#         self.assertEqual(result, self.tag)

#     async def test_get_tags(self):
#         self.db.query.return_value.all.return_value = [self.tag]

#         result = await get_tags(db=self.db)
#         self.db.query.assert_called_once_with(Tag)
#         self.assertEqual(result, [self.tag])

#     async def test_remove_tag(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = self.tag
#         self.db.delete = AsyncMock()
#         self.db.commit = AsyncMock()

#         await remove_tag(tag_id=1, db=self.db)
#         self.db.query.assert_called_once_with(Tag)
#         self.db.delete.assert_called_once()
#         self.db.commit.assert_called_once()

#     async def test_remove_tag_not_found(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = None

#         with self.assertRaises(HTTPException) as context:
#             await remove_tag(tag_id=1, db=self.db)
        
#         self.assertEqual(context.exception.status_code, 404)
#         self.db.query.assert_called_once_with(Tag)

#     async def test_update_tag(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = self.tag
#         self.db.commit = AsyncMock()

#         await update_tag(tag_id=1, body=self.body, db=self.db)
#         self.db.query.assert_called_once_with(Tag)
#         self.db.commit.assert_called_once()

#     async def test_update_tag_not_found(self):
#         self.db.query.return_value.filter_by.return_value.first.return_value = None

#         with self.assertRaises(HTTPException) as context:
#             await update_tag(tag_id=1, body=self.body, db=self.db)
        
#         self.assertEqual(context.exception.status_code, 404)
#         self.db.query.assert_called_once_with(Tag)

import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from photoshare.database.models import Tag
from photoshare.repository.tags import create_tag, get_tag, remove_tag, update_tag, get_tags
from photoshare.schemas import TagModel

class TestTagRepository(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db = MagicMock()
        self.body = TagModel(name="good")
        self.tag = Tag(id=1, name='test')

    async def test_create_tag(self):
        tag = Tag(name="good")
        self.db.query().filter().first.return_value = None
        new_tag = await create_tag(body=tag, db=self.db)
        self.assertEqual(new_tag.name, tag.name)
        self.assertTrue(hasattr(new_tag, "id"))

    async def test_create_tag_already_exists(self):
        self.db.query().filter().first.return_value = True

        with self.assertRaises(HTTPException) as context:
            await create_tag(body=self.body, db=self.db)
        
        self.assertEqual(context.exception.status_code, 400)

    async def test_get_tag(self):
        self.db.query.return_value.filter_by.return_value.first.return_value = self.tag

        result = await get_tag(tag_id=1, db=self.db)
        self.db.query.assert_called_once_with(Tag)

    # async def test_get_tags(self):
    #     tags = [Tag(), Tag()]
    #     self.db.query().offset().limit().all = tags

    #     result = await get_tags(skip = 0, limit=10, db=self.db)
    #     self.db.query.assert_called_once_with(Tag)
    #     self.assertEqual(result, tags)

    async def test_remove_tag(self):
        self.db.query.return_value.filter_by.return_value.first.return_value = self.tag
        self.db.delete = AsyncMock()
        self.db.commit = AsyncMock()

        await remove_tag(tag_id=1, db=self.db)
        self.db.delete.assert_called_once()
        self.db.commit.assert_called_once()

    async def test_remove_tag_not_found(self):
        self.db.query().filter().first.return_value = None

        res = await remove_tag(tag_id=1, db=self.db)
        
        self.assertIsNone(res)

    async def test_update_tag(self):
        self.db.query().filter().first.return_value = self.tag

        await update_tag(tag_id=1, body=self.body, db=self.db)
        self.db.commit.assert_called_once()

    async def test_update_tag_not_found(self):
        self.db.query().filter().first.return_value = None

        res = await update_tag(tag_id=1, body=self.body, db=self.db)
        
        self.assertIsNone(res)


