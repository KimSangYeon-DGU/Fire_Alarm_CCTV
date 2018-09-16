from pyfcm import FCMNotification

push_service = FCMNotification(api_key="Server-key")

# Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "Registration-key"
message_title = "Fire was detected"
message_body = "Please check your CCTV App"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

print(result)