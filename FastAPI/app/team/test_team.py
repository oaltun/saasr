from app.team.schema import TeamOut


def test_create_team(test_team):
    assert test_team.recurring_billing_is_on == True


