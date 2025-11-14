def test_all(journal_repository, example_logs):
    logs = journal_repository.all()
    
    assert len(logs) == len(example_logs)
    
    for i in range(len(logs)):
        assert logs[i].id == example_logs[i].id
        assert logs[i].path == example_logs[i].path
        assert logs[i].user_id == example_logs[i].user_id
        assert logs[i].created_at == example_logs[i].created_at

def test_all_by_id(journal_repository, example_logs):
    test_user_id = example_logs[0].user_id
    logs = journal_repository.all_by_id(test_user_id)

    counter = 0
    for i in range(len(logs)):
        if example_logs[i].user_id == test_user_id:
            counter += 1
            assert logs[i].id == example_logs[i].id
            assert logs[i].path == example_logs[i].path
            assert logs[i].created_at == example_logs[i].created_at
    assert counter == len(logs)
        

def test_get_total_count(journal_repository, example_logs):
    total_count = journal_repository.get_total_count()
    
    assert total_count == len(example_logs) 

def test_get_total_count_by_id(journal_repository, example_logs):
    test_user_id = example_logs[0].user_id
    total_count = journal_repository.get_total_count_by_user_id(test_user_id)
    
    counter = 0
    for i in range(len(example_logs)):
        if example_logs[i].user_id == test_user_id:
            counter += 1

    assert total_count == counter 

def test_get_page(journal_repository, example_logs):
    test_per_page = 10
    test_page = 1
    
    pages = journal_repository.get_page(test_per_page, test_page)

    sorted_example_logs = sorted(example_logs, key=lambda item: item.id, reverse=True)
    
    counter = 0
    for index, page in enumerate(pages):
        counter += 1
        assert page.id == sorted_example_logs[index].id
        assert page.path == sorted_example_logs[index].path
        assert page.created_at == sorted_example_logs[index].created_at
    
    assert test_per_page == counter

def test_get_page_by_id(journal_repository, example_logs):
    test_per_page = 10
    test_page = 1
    test_user_id = example_logs[0].user_id

    pages = journal_repository.get_page_by_user_id(test_user_id, test_per_page, test_page)

    sorted_example_logs = sorted(example_logs, key=lambda item: item.id, reverse=True)
    sorted_example_logs_by_user_id = []
    for log in sorted_example_logs:
        if log.user_id == test_user_id:
            sorted_example_logs_by_user_id.append(log)

    counter = 0
    for index, page in enumerate(pages):
        counter += 1
        assert page.id == sorted_example_logs_by_user_id[index].id
        assert page.path == sorted_example_logs_by_user_id[index].path
        assert page.created_at == sorted_example_logs_by_user_id[index].created_at
    
    assert test_per_page == counter

def test_log_page_aggregation(journal_repository, example_logs):
    db_statistics = journal_repository.log_page_aggregation()

    manual_statistics = {}
    for stat in example_logs:
        if stat.path not in manual_statistics:
            manual_statistics[stat.path] = 1
        else:
            manual_statistics[stat.path] += 1

    manual_statistics = dict(sorted(manual_statistics.items(), key=lambda item: item[1], reverse=True))

    assert len(db_statistics) == len(manual_statistics)

    for index, stat in enumerate(manual_statistics):
        assert db_statistics[index].path in manual_statistics.keys()
        assert db_statistics[index].number_of_visits == manual_statistics[db_statistics[index].path]


def test_log_page_aggregation_with_user_id(journal_repository, example_logs):
    db_statistics = journal_repository.log_page_aggregation(example_logs[0].user_id)

    manual_statistics = {}
    for stat in example_logs:
        if stat.user_id == example_logs[0].user_id:
            if stat.path not in manual_statistics:
                manual_statistics[stat.path] = 1
            else:
                manual_statistics[stat.path] += 1

    manual_statistics = dict(sorted(manual_statistics.items(), key=lambda item: item[1], reverse=True))

    assert len(db_statistics) == len(manual_statistics)

    for index, stat in enumerate(manual_statistics):
        assert db_statistics[index].path in manual_statistics.keys()
        assert db_statistics[index].number_of_visits == manual_statistics[db_statistics[index].path]

def test_log_user_aggregation(journal_repository, example_logs, user_repository):
    db_statistics = journal_repository.log_user_aggregation()

    manual_statistics = {}
    for stat in example_logs:
        if stat.user_id == None:
            user = 'Неаутентифицированный пользователь'
        else:
            user_data = user_repository.get_by_id(stat.user_id)
            user = f'{user_data.last_name} {user_data.first_name} {user_data.middle_name if user_data.middle_name != None else ''}'.strip()
        if user not in manual_statistics:
            manual_statistics[user] = 1
        else:
            manual_statistics[user] += 1

    manual_statistics = dict(sorted(manual_statistics.items(), key=lambda item: item[1], reverse=True))

    assert len(db_statistics) == len(manual_statistics)

    for index, stat in enumerate(manual_statistics):
        assert db_statistics[index].user_full_name in manual_statistics.keys()
        assert db_statistics[index].number_of_visits == manual_statistics[db_statistics[index].user_full_name]

def test_log_user_aggregation_by_user_id(journal_repository, example_logs, user_repository):
    db_statistics = journal_repository.log_user_aggregation(example_logs[0].user_id)

    manual_statistics = {}
    for stat in example_logs:
        if stat.user_id == example_logs[0].user_id:
            user_data = user_repository.get_by_id(stat.user_id)
            user = f'{user_data.last_name} {user_data.first_name} {user_data.middle_name if user_data.middle_name != None else ''}'.strip()
            
            if user not in manual_statistics:
                manual_statistics[user] = 1
            else:
                manual_statistics[user] += 1

    manual_statistics = dict(sorted(manual_statistics.items(), key=lambda item: item[1], reverse=True))

    assert len(db_statistics) == len(manual_statistics)

    for index, stat in enumerate(manual_statistics):
        assert db_statistics[index].user_full_name in manual_statistics.keys()
        assert db_statistics[index].number_of_visits == manual_statistics[db_statistics[index].user_full_name]