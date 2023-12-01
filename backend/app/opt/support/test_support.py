from app.opt.support import schema


def new_issue(client, headers, title, message_text):
        res = client.post(
            "/api/v1/support_issues",
            json={"title": title, "message_text": message_text},
            headers=headers,
        )

        issue = schema.IssueOut(**res.json())
        assert issue.title == title
        assert res.status_code == 201
        return issue


def test_create_issue(client,user_token_headers):
    issue = new_issue(client, user_token_headers, "some title", "some message text")


def test_issue_has_close_info(client, user_token_headers, superuser_token_headers):
    issue = new_issue(client, user_token_headers, "some title 1", "some message text 1")
    issue_id = str(issue.id)
    assert issue.closer == None
    assert issue.is_closed == False

    ## add a second message to the issue
    res = client.post(
        "/api/v1/support_messages",
            json={
                "issue_id": issue_id, 
                "text": "some message text 2"
            },
            headers=superuser_token_headers,
    )
    message = schema.MessageOut(**res.json())

    ## super user closes the issue
    res = client.put(
        f"/api/v1/support_issues/{issue_id}",
            json={
                "is_closed": True, 
            },
            headers=superuser_token_headers,
    )
    issue_closed = schema.IssueOut(**res.json())
    assert issue_closed.is_closed == True

    ## try adding a new message  to the issue. Since the issue is closed, it should not be possible.
    res = client.post(
        "/api/v1/support_messages",
            json={
                "issue_id": issue_id, 
                "text": "some message text 3"
            },
            headers=superuser_token_headers,
    )
    print("res.status_codde",res.status_code)

    ## super user closes the issue again. Should not be possible, as issue is already closed
    res = client.put(
        f"/api/v1/support_issues/{issue_id}",
            json={
                "is_closed": True, 
            },
            headers=superuser_token_headers,
    )
    print("res.statuss_codde",res.status_code)

    ## super user tries to reopen the issue. Should not be allowed.
    res = client.put(
        f"/api/v1/support_issues/{issue_id}",
            json={
                "is_closed": False, 
            },
            headers=superuser_token_headers,
    )
    print("res.status_coddddde",res.status_code)




    
def test_list_issues(client, user_token_headers, superuser_token_headers):
    title1 = "some title 1"
    issue1 = new_issue(client, user_token_headers, title1, "some message text 1")    
    
    issue2 = new_issue(client, user_token_headers, "some title 2", "some message text 2")

    ## super user tries to reopen the issue. Should not be allowed.
    res = client.get("/api/v1/support_issues",
        headers=user_token_headers,
    )
    issues = [schema.IssueOutInList(**issue_json) for issue_json in res.json()]
    assert issues[0].title == title1
 

