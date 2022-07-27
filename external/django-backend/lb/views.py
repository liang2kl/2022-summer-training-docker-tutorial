from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(utils.get_leaderboard(), safe=False)


@method(["GET"])
def history(req: HttpRequest, username: int):
    try:
        res = User.objects.get(username=username)
        return JsonResponse({
            "code": 0,
            "data": [
                {
                    **model_to_dict(s, exclude=["id", "subs", "user"]),
                    "subs": [int(x) for x in s.subs.split()]
                }
                for s in res.submission_set.all().order_by('-time')
            ]
        })

    except:
        return JsonResponse({
            "code": -1
        })


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    try:
        req = json.loads(req.body)
        if not ('user' in req and 'avatar' in req and 'content' in req):
            return JsonResponse({
                "code": 1,
                "msg": "参数不全啊"
            })

        if len(req['user']) >= 255:
            return JsonResponse({
                "code": -1,
                "msg": "用户名太长了"
            })

        if len(req['avatar']) >= 500000:
            return JsonResponse({
                "code": -2,
                "msg": "图像太大了"
            })

        try:
            score, subs = utils.judge(req["content"])
        except:
            return JsonResponse({
                "code": -3,
                "msg": "提交内容非法"
            })

        usr = User.objects.filter(username=req["user"]).first()
        if not usr:
            usr = User.objects.create(username=req["user"])
    except:
        if settings.DEBUG:
            raise
        return JsonResponse({
            "code": 2,
            "msg": "不太对劲"
        })

    Submission.objects.create(
        user=usr,
        avatar=req['avatar'],
        score=score,
        subs=" ".join(map(str, subs)),
    )

    return JsonResponse({
        "code": 0,
        "msg": "提交成功",
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })

    try:
        req = json.loads(req.body)
        user = req['user']
        usr = User.objects.get(username=user)
    except:
        return JsonResponse({
            "code": -1
        }, status=400)

    usr.votes = F("votes") + 1
    usr.save()

    return JsonResponse({
        "code": 0,
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    }, safe=False)
