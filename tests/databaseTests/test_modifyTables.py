import pytest
from modifyTables import allowlist_modifyTables
from MT_test_helpers import gen_random_strings

"""
Functions to test:
    allowlist_modifyTables.create_organization_table()
    allowlist_modifyTables.read_repo()
    allowlist_modifyTables.read_repo_with_info()
    allowlist_modifyTables.insert_new_term()
    allowlist_modifyTables.insert_new_terms()
    allowlist_modifyTables.insert_new_terms_with_info()
    allowlist_modifyTables.delete_term()
    allowlist_modifyTables.delete_repo()
    allowlist_modifyTables.delete_table()
"""
org_id = "123456"

@pytest.fixture
def create_table(db_resource):
    allowlist_modifyTables.create_organization_table(org_id, dynamodb=db_resource)
    yield

def test_create_table(db_resource):
    allowlist_modifyTables.create_organization_table(org_id, dynamodb=db_resource)
    tables = list(db_resource.tables.all())
    assert len(tables) == 1
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 0 

def test_integration():
    assert True

