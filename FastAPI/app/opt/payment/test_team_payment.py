from app.team.schema import TeamOut


def test_team_invitation(
    initial_payment, 
    client,
    user_token_headers
    ):

    team_id = str(initial_payment.team_id)

    ## invite somebody to this team
    body = {
        "team_id": team_id,
        "email": "abc@gmail.com",
        "is_admin": False
    }
    print("body:",body)
    res_invitation_create = client.post("/api/v1/team_invitations", json=body, headers=user_token_headers)
    
    
    ## see if the invited person is in the team invitations
    res_team_query = client.get(f"/api/v1/teams/{team_id}", headers=user_token_headers)
    team = TeamOut(**res_team_query.json())


    assert team.invitations[0].email == "abc@gmail.com"


def test_team_invitation_single_license(
    initial_payment_single_license, 
    client,
    user_token_headers
    ):

    team_id = str(initial_payment_single_license.team_id)
    def invite(email, is_admin):
        body = {
            "team_id": team_id,
            "email": email,
            "is_admin": is_admin
        }
        return client.post("/api/v1/team_invitations", json=body, headers=user_token_headers)


    #### invite 2 admins and one licensee to this team
    res = invite("admin1@gmail.com", True)
    print("test_team_invitation_single_license:",res.status_code)
    assert res.status_code ==201

    res = invite("admin2@gmail.com", True)
    print("test_team_invitation_single_license:",res.status_code)
    assert res.status_code ==201

    res = invite("member1@gmail.com", False)
    print("test_team_invitation_single_license:",res.status_code)
    assert res.status_code ==201

    #### invite a second member. We have only one license. So should not be ok.
    res = invite("member2@gmail.com", False)
    print("test_team_invitation_single_license:",res.status_code)
    assert res.status_code ==406
    #### TODO: let admin1 and member1 accept invitations

    #### TODO: test admin2 reject invitation

    #### TODO: test member1 reject invitation

    #### TODO: test removal of admin1,2 and member1


    #### see if the invited people are in the team invitations
    res_team_query = client.get(f"/api/v1/teams/{team_id}", headers=user_token_headers)
    team = TeamOut(**res_team_query.json())

    print("Final team: ", team)







def test_team_invitation_get_invitation(
    initial_payment, 
    client,
    test_user,
    test_user2,
    user_token_headers,
    user2_token_headers
    ):

    team_id = str(initial_payment.team_id)
    def invite(email, is_admin):
        body = {
            "team_id": team_id,
            "email": email,
            "is_admin": is_admin
        }
        return client.post("/api/v1/team_invitations", json=body, headers=user_token_headers)


    #### invite user 2 to this team
    res = invite(test_user2.email, is_admin=False)
    assert res.status_code == 201

    # user2 checks their invitations
    res = client.get(f"/api/v1/team_invitations", headers=user2_token_headers)
    print("res: ", res)
    print("res.json():")
    from pprint import pprint
    pprint(res.json())

    from typing import List
    from app.team.schema import TeamInvitationOut
    # a = List[TeamInvitationOut](**res.json())
    invitation = TeamInvitationOut(**res.json()[0])

    assert invitation.email == test_user2.email
    assert invitation.team.id == initial_payment.team_id
    assert invitation.inviter.id == test_user.id