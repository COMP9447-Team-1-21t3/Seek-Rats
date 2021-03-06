import pytest
from modifyTables import allowlist_modifyTables
from MT_test_helpers import gen_random_strings

"""
Functions to test:
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

def test_insert_new_terms(db_resource, setup_repo):
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    terms = gen_random_strings(50)
    allowlist_modifyTables.insert_new_terms(org_id, repo_id, terms, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 51

    tterms = allowlist_modifyTables.read_repo(org_id, repo_id, dynamodb=db_resource)
    assert len(terms) == len(tterms)
    assert all(elem in terms for elem in tterms)

def test_insert_new_terms_with_info(db_resource, setup_repo):
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    terms = gen_random_strings(50)
    terms = [{'term':x, 'info': {'term':x}} for x in terms]
    allowlist_modifyTables.insert_new_terms_with_info(org_id, repo_id, terms, dynamodb=db_resource)

    table = db_resource.Table(tableName)
    assert table.item_count == 51
    tterms = allowlist_modifyTables.read_repo(org_id, repo_id, dynamodb=db_resource)
    assert len(terms) == len(tterms)
    assert all(elem['term'] in tterms for elem in terms)


def test_read_repo_with_info(db_resource, setup_repo):
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    term = "hello"
    allowlist_modifyTables.insert_new_term(org_id, repo_id, term, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 2

    terms = allowlist_modifyTables.read_repo_with_info(org_id, repo_id, dynamodb=db_resource)
    assert len(terms) == 1
    assert terms[0] == {'term':term, 'info':{}}

    terms = gen_random_strings(50)
    terms = [{'term':x, 'info': {'term':x}} for x in terms]
    allowlist_modifyTables.insert_new_terms_with_info(org_id, repo_id, terms, dynamodb=db_resource)

    tterms = allowlist_modifyTables.read_repo_with_info(org_id, repo_id, dynamodb=db_resource)
    assert len(terms)+1 == (len(tterms)) 

def test_delete_repo(db_resource, setup_repo):
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    allowlist_modifyTables.delete_repo(org_id, repo_id, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 0

    allowlist_modifyTables.setup_new_repo(org_id, repo_id, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    terms = gen_random_strings(500)
    allowlist_modifyTables.insert_new_terms(org_id, repo_id, terms, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == len(terms) + 1

    allowlist_modifyTables.delete_repo(org_id, repo_id, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 0

def test_delete_term(db_resource, setup_repo):
    tableName = f"{allowlist_modifyTables.tablename_prefix}_{org_id}"
    table = db_resource.Table(tableName)
    assert table.item_count == 1

    term = "hello"
    allowlist_modifyTables.insert_new_term(org_id, repo_id, term, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 2

    allowlist_modifyTables.delete_term(org_id, repo_id, term, dynamodb=db_resource)
    table = db_resource.Table(tableName)
    assert table.item_count == 1

def test_delete_table(db_resource, create_table):
    allowlist_modifyTables.delete_table(org_id, dynamodb=db_resource)
    tables = list(db_resource.tables.all())
    assert len(tables) == 0

def test_functions_without_setup(db_resource):
    assert True