# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import meetingmode.routing, studymode.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            meetingmode.routing.websocket_urlpatterns +
            studymode.routing.websocket_urlpatterns
        )
    ),
})