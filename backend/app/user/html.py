from app.config import settings

def password_reset_request(email, hash_code):    
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Hi there!</p>
            <p>We received a request to reset your password.</p>
            <p>Please copy and paste following code into the code field in password reset page:</p>

            <p>{hash_code}</p>

            <p>This code is valid for {settings.PASSWORD_RESET_VALID_FOR_HOURS} hours.</p>
            <p>Ignore this email if this was not your request. No changes have been made to your account yet.</p>
            <p>Yours sincerely,</p>
            <p>Oguz from SAASR.</p>
        </body>
        </html>
        """


def verify_request(email, hash_code):
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Thanks for signing up!</p>

            <p>Your account has been created.</p>
            
            <p>Please copy/paste following code to verify your email:</p>

            <p>{hash_code}</p>

            <p>This code is valid for {settings.EMAIL_VERIFICATION_VALID_FOR_HOURS} hours.</p>
            
            <p>Yours sincerely,</p>
            <p>Oguz from SAASR.</p>
        </body>
        </html>
        """
    

def invite_to_team(email, user_full_name, team_name,invitation_id):
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Hi!</p>
            <p>You are invited to the team {team_name} (invitation id: {invitation_id}).</p>
            <p>To accept the invitation login to the SAASR Exam Add-In backend system. You will see a pop-up that will enable accepting this invitation.</p>
           
            <p>Note that you will need to sign-up as a SAASR user to login the system.</p>

            <p>Yours sincerely,</p>
            <p>Oguz from SAASR.</p>
        </body>
        </html>
        """
