# from django.test import TestCase
from twilio.rest import Client
# # Create your tests here.
# sid = 'AC084b5688bec2a5207f2ffdd6e095e941'
# auth_id = 'dc163abc5da55417accbedeaaed06327'
# v_sid = 'VA9bb04eb8dbde3653dc14d96843a7e050'
# t_client = Client(sid,auth_id)

# # verification = t_client.verify.services(v_sid) \
# #                                     .verifications \
# #                                     .create(to=f'+919404641400',channel='sms')

# check = t_client.verify.services(v_sid) \
#                             .verification_checks \
#                                 .create(to='+919404641400',code=150074)

# print(check.status)

# from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'AC084b5688bec2a5207f2ffdd6e095e941'
auth_token = 'dc163abc5da55417accbedeaaed06327'
client = Client(account_sid, auth_token)

# Create a new verification service
service = client.verify.services.create(
    friendly_name='Greenfield'
)

# Print the service SID
print(service.sid)

# s_id = 'VA9bd0ecb8564389a81892f8142b96919b'