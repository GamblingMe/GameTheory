# coding:utf-8

from imp import reload
import json
import random
from time import time
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

id_now = -1


def generate_id():
    global id_now
    id_now += 1
    return id_now


default_evaluator = '''adds = [1] * len(result)'''


class Game:
    def __init__(self, title, question, selections: list[str], start_timestamp_msec=0,
                 duration_msec=0, status="finished", evaluator=default_evaluator):
        self.gid = generate_id()
        self.title = title
        self.question = question
        self.selections = selections
        self.allocations = []
        self.result = []
        for i in range(len(self.selections)):
            self.allocations.append(set())
            self.result.append(0.0)
        # status: waiting, started, finished
        self.status = status
        self.evaluator = default_evaluator if len(evaluator) == 0 else evaluator
        self.start_timestamp_msec = start_timestamp_msec
        self.duration_msec = duration_msec
        self.participants = set()


# class GameResp(BaseModel):
#     gid: int
#     title: str
#     question: str
#     selections: str
#     allocations: list[set]
#     result: list[float]
#     status: str
#     start_timestamp_msec: int
#     duration_msec: int
#     participants: set[str]


# def game_to_resp(game: Game) -> GameResp:
#     return GameResp(gid=game.gid, title=game.title, question=game.question, selections=game.selections,
#                     allocations=game.allocations, result=game.result, status=game.status,
#                     start_timestamp_msec=game.start_timestamp_msec,
#                     duration_msec=game.duration_msec, participants=game.participants)


games = {}

accounts = {}


@app.on_event("startup")
async def startup():
    if os.path.exists("data.json"):
        print("Loading games from file...")
        global games, accounts
        data = json.load(open("games.data.json", 'r'))
        games = data["games"]
        accounts = data["accounts"]
    else:
        print("Creating new games...")


@app.on_event("shutdown")
async def shutdown():
    print("Saving games to file...")
    data = {"games": games, "accounts": accounts}
    json.dump(data, open("games.data.json", 'w'))


class SubmitItem(BaseModel):
    selection: int
    timestamp: int
    user_id: str


class GameHttp(BaseModel):
    title: str
    question: str
    selections: list[str]
    start_timestamp_msec: int
    duration_msec: int
    evaluator: str


def update_score(game):
    evaluator = game.evaluator
    alloc = [0] * len(game.selections)
    for i in range(len(alloc)):
        alloc[i] = len(game.allocations[i])
    local = {}
    exec(evaluator, {'result': alloc}, local)
    eval_res = local['adds']
    game.result = eval_res
    for i in range(len(game.allocations)):
        for uid in game.allocations[i]:
            accounts[uid] += eval_res[i]


def update_game_status(gid: int):
    global games
    game = games[gid]
    if time() * 1000 - game.start_timestamp_msec > game.duration_msec:
        if game.status != "finished":
            update_score(game)
        game.status = "finished"
    elif game.status == "waiting":
        game.status = "started"


animals = "虎、狼、鼠、鹿、貂、猴、树懒、斑马、狗、狐、豹子、麝牛、狮子、疣猪、考拉、犀牛、猞猁、穿山甲、长颈鹿、熊猫、食蚁兽、猩猩、海牛、灵猫、海豚、海象、鸭嘴兽、刺猬、北极狐、无尾熊、北极熊、袋鼠、犰狳、河马、海豹、鲸鱼、鼬".split(
    '、')


def randname():
    return random.choice(animals) + "#" + str(random.randint(1000, 10000))


@app.get("/rand_username")
def rand_username():
    i = 0
    while i < 20:
        name = randname()
        if name not in accounts:
            accounts[name] = 10
            return {"username": name, "status": "ok"}
        i += 1
    return {"status": "error", "message": "too many duplicates, try again later"}


@app.get("/rank")
def rank():
    return {"status": "ok", "rank": accounts}


@app.get("/games_titles")
def games_titles():
    gms = []
    for game in games.values():
        if game.status == "finished":
            gms.append(game.title)
    return {"status": "ok", "games": gms}


@app.post("/new_game")
async def new_game(new_game: GameHttp, key: str = ''):
    global games, chats
    if key != os.environ.get('GT_KEY'):
        return {"status": "error", "message": "invalid key"}
    if id_now != -1 and games[id_now].status != "finished":
        return {"status": "error", "message": "game already exists"}
    game = Game(new_game.title, new_game.question, new_game.selections, new_game.start_timestamp_msec,
                new_game.duration_msec, "started", new_game.evaluator)
    games[game.gid] = game
    update_game_status(game.gid)
    chats = []
    return game


def query_selection_and_result(gid: int, uid: str):
    global games
    game = games[gid]
    for i in range(len(game.selections)):
        if uid in game.allocations[i]:
            return {"selection": i, "result": game.result[i]}
    return {"selection": -1, "result": 0}


@app.get("/game/{gid}/user/{uid}")
def game_user(gid: int, uid: str):
    global games
    if gid not in games:
        return {"status": "error", "message": "game not found"}
    game = games[gid]
    sr = query_selection_and_result(gid, uid)
    return {"game": game, "status": "ok", "user_selection": sr["selection"], "result": sr["result"]}


@app.get("/game/{gid}", response_model_exclude={"status"})
def get_game(gid: int):
    global games
    if gid not in games:
        return {"status": "error", "message": "game not found"}
    game = games[gid]
    return {"status": "ok", "game": (game)}


@app.post("/submits")
async def submit(submit: SubmitItem):
    global games
    update_game_status(id_now)
    print(f"{submit.user_id} submitted {submit.selection} at {submit.timestamp}")
    game = games[id_now]
    if game.status != "started":
        return {"status": f"invalid operation, game is {game.status}"}
    dup_flag = False
    for allocation in game.allocations:
        if submit.user_id in allocation:
            allocation.remove(submit.user_id)
    if dup_flag:
        return {"status": "duplicate"}
    game.allocations[submit.selection].add(submit.user_id)
    game.participants.add(submit.user_id)
    if submit.user_id not in accounts:
        accounts[submit.user_id] = 10
    return {"status": "ok"}


@app.get("/score/{username}")
def score(username: str):
    if username in accounts:
        return {"status": "ok", "score": accounts[username]}
    else:
        return {"status": "error", "message": "user not found"}


@app.get("/submits")
def get_submits(username: str = "") -> Game:
    global games
    if id_now == -1:
        return {"status": "error", "message": "no game in progress currently"}
    update_game_status(id_now)
    game = games[id_now]
    gu = query_selection_and_result(id_now, username)
    return {"status": "ok", "game": game, "user_score": -1 if username not in accounts else accounts[username],
            "user_selection": gu["selection"], "result": gu["result"]}
