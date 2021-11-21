import pytest
from modifyTables import allowlist_modifyTables
from MT_test_helpers import gen_random_strings

"""
Functions to test:
    allowlist_modifyTables.read_repo_with_info()
    allowlist_modifyTables.insert_new_term()
    allowlist_modifyTables.insert_new_terms()
    allowlist_modifyTables.insert_new_terms_with_info()
    allowlist_modifyTables.delete_term()
    allowlist_modifyTables.delete_repo()
    allowlist_modifyTables.delete_table()
"""
org_id = "123456"

def test_create_table(db_resource):
    # allowlist_modifyTables.create_organization_table()
    assert allowlist_modifyTables.create_organization_table(org_id, dynamodb=db_resource)
    tables = list(db_resource.tables.all())
    assert len(tables) == 1
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 0 

@pytest.fixture
def create_table(db_resource):
    allowlist_modifyTables.create_organization_table(org_id, dynamodb=db_resource)
    yield

repo_id = "654321"

def test_setup_new_repo(db_resource, create_table):
    #allowlist_modifyTables.setup_new_repo()
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 0 
    allowlist_modifyTables.setup_new_repo(org_id, repo_id, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 1
    with pytest.raises(ValueError) as e:
        allowlist_modifyTables.setup_new_repo(org_id, repo_id, dynamodb=db_resource)
    assert "already initialized" in str(e.value)
    table = db_resource.Table(tableName)
    assert table.item_count == 1

@pytest.fixture
def setup_repo(db_resource, create_table):
    allowlist_modifyTables.setup_new_repo(org_id, repo_id, dynamodb=db_resource)
    yield

def test_insert_new_term(db_resource, setup_repo):
    #allowlist_modifyTables.insert_new_term()
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    term = "hello"
    allowlist_modifyTables.insert_new_term(org_id, repo_id, term, dynamodb=db_resource)

    table = db_resource.Table(tableName)
    assert table.item_count == 2

    allowlist_modifyTables.insert_new_term(org_id, repo_id, term, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 2

def test_read_repo(db_resource, setup_repo):
    #allowlist_modifyTables.read_repo()
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    terms = allowlist_modifyTables.read_repo(org_id, repo_id, dynamodb=db_resource)
    assert len(terms) == 0

    term = "hello"
    allowlist_modifyTables.insert_new_term(org_id, repo_id, term, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 2

    terms = allowlist_modifyTables.read_repo(org_id, repo_id, dynamodb=db_resource)
    assert len(terms) == 1
    assert terms[0] == term
    
def test_functions_without_setup(db_resource):
    assert True