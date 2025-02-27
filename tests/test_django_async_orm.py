from unittest import IsolatedAsyncioTestCase

from django.apps import apps
from django.test import TestCase, TransactionTestCase, tag

from .models import TestModel


class AppLoadingTestCase(TestCase):
    @tag("ci")
    def test_dao_loaded(self):
        self.assertTrue(apps.is_installed("django_async_orm"))

    @tag("ci")
    def test_manager_is_async(self):
        manager_class_name = TestModel.objects.__class__.__name__
        self.assertTrue(
            manager_class_name.startswith("MixinAsync"),
            'Manager class name is %s but should start with "MixinAsync"'
            % (manager_class_name),
        )


class ModelTestCase(TransactionTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await TestModel.objects.async_create(name="setup 1", obj_type="setup")
        await TestModel.objects.async_create(name="setup 2", obj_type="setup")

    async def asyncTearDown(self):
        await TestModel.objects.async_delete()

    @tag("ci")
    async def test_async_get(self):
        result = await TestModel.objects.async_get(name="setup 1")
        self.assertEqual(result.name, "setup 1")

    @tag("ci")
    async def test_async_create(self):
        result = await TestModel.objects.async_create(name="test")
        self.assertEqual(result.name, "test")

    @tag("ci")
    async def test_async_bulk_create(self):
        objs = await TestModel.objects.async_bulk_create(
            [
                TestModel(name="bulk create 1"),
                TestModel(name="bulk create 2"),
            ]
        )
        objs = await TestModel.objects.async_all()
        objs = await objs.async_count()
        self.assertEqual(objs, 4)

    @tag("dev")
    async def test_async_bulk_update(self):
        self.assertTrue(False, "Not Implemented")

    @tag("ci")
    async def test_async_get_or_create(self):
        async def test_async_get_or_create_on_obj_get(self):
            obj = await TestModel.objects.async_get_or_create(name="setup 1")
            self.assertEqual(obj[1], False)

        async def test_async_get_or_create_on_obj_create(self):
            obj = await TestModel.objects.async_get_or_create(name="setup 3")
            self.assertEqual(obj[0].name, "setup 3")
            self.assertEqual(obj[1], True)

        await test_async_get_or_create_on_obj_get(self)
        await test_async_get_or_create_on_obj_create(self)

    @tag("dev")
    async def test_async_update_or_create(self):
        self.assertTrue(False, "Not Implemented")

    @tag("ci")
    async def test_async_earliest(self):
        first = await (await TestModel.objects.async_all()).async_first()
        earliest = await TestModel.objects.async_earliest("id")
        self.assertTrue(earliest.id, first.id)

    @tag("ci")
    async def test_async_latest(self):
        created = await TestModel.objects.async_create(name="latest")
        latest = await TestModel.objects.async_latest("id")
        self.assertEqual(latest.id, created.id)

    @tag("ci")
    async def test_async_first_in_all(self):
        all_result = await TestModel.objects.async_all()
        first = await all_result.async_first()
        self.assertEqual(all_result[0].name, first.name)

    @tag("ci")
    async def test_async_last_in_all(self):
        all_result = await TestModel.objects.async_all()
        last = await all_result.async_last()
        self.assertEqual(all_result[1].name, last.name)

    @tag("dev")
    async def test_async_in_bulk(self):
        self.assertTrue(False, "Not Implemented")

    @tag("ci")
    async def test_async_delete(self):
        created = await TestModel.objects.async_create(name="to delete")
        all_created = await TestModel.objects.async_all()
        count = await all_created.async_count()
        self.assertEqual(count, 3)

        await all_created.async_delete()
        all_after_delete = await TestModel.objects.async_all()
        count = await all_after_delete.async_count()
        self.assertEqual(count, 0)

    @tag("ci")
    async def test_async_update(self):
        created = await TestModel.objects.async_create(name="to update")
        qs = await TestModel.objects.async_filter(name="to update")
        updated = await qs.async_update(name="updated")
        self.assertEqual(updated, 1)

    @tag("ci")
    async def test_async_exists(self):
        qs = await TestModel.objects.async_filter(name="setup 1")
        exists = await qs.async_exists()
        self.assertTrue(exists)

    @tag("ci")
    async def test_async_explain(self):
        explained = await (
            await TestModel.objects.async_filter(name="setup 1")
        ).async_explain()
        print(explained)
        self.assertEqual(explained, "2 0 0 SCAN tests_testmodel")

    @tag("dev")
    async def test_async_raw(self):
        rs = await TestModel.objects.async_raw("SELECT * from tests_testmodel")
        print(list(rs))

    @tag("ci")
    async def test_async_count(self):
        result = await TestModel.objects.async_all()
        result = await result.async_count()
        self.assertEqual(result, 2)

    @tag("ci")
    async def test_async_none(self):
        result = await TestModel.objects.async_none()
        self.assertEqual(list(result), [])

    @tag("ci")
    async def test_async_aiter(self):
        all_qs = await TestModel.objects.async_all()
        count = 0
        async for obj in all_qs:
            count += 1
        self.assertEqual(count, 2)

    @tag("dev")
    async def test_async_fetch_all(self):
        self.assertTrue(False, "Not Implemented")

    @tag("ci")
    async def test_async_all(self):
        result = await TestModel.objects.async_all()
        result = await result.async_count()
        self.assertEqual(result, 2)

    @tag("ci")
    async def test_async_filter(self):
        qs = await TestModel.objects.async_filter(name="setup 2")
        element = await qs.async_first()
        self.assertEqual(element.name, "setup 2")

    @tag("ci")
    async def test_async_exclude(self):
        qs = await TestModel.objects.async_filter(obj_type="setup")
        qs = await qs.async_exclude(name="setup 1")
        el = await qs.async_first()
        self.assertEqual(el.name, "setup 2")

    @tag("dev")
    async def test_async_complex_filter(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_union(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_intersection(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_difference(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_select_for_update(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_prefetch_related(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_annotate(self):
        self.assertTrue(False, "Not Implemented")

    @tag("ci")
    async def test_async_order_by_ascending(self):
        qs = await TestModel.objects.async_all()
        qs = await qs.async_order_by("name")
        qs = await qs.async_first()
        self.assertEqual(qs.name, "setup 1")

    @tag("ci")
    async def test_async_order_by_descending(self):
        qs = await TestModel.objects.async_all()
        qs = await qs.async_order_by("-name")
        qs = await qs.async_first()
        self.assertEqual(qs.name, "setup 2")

    @tag("dev")
    async def test_async_distinct(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_extra(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_reverse(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_defer(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_only(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_using(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_resolve_expression(self):
        self.assertTrue(False, "Not Implemented")

    @tag("dev")
    async def test_async_async_ordered(self):
        self.assertTrue(False, "Not Implemented")
