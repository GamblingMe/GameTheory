<template>
  <el-container id="container">
    <el-col>
      <el-row>
        <el-tree-select
          v-model="selected"
          :data="history"
          :props="props"
          placeholder="选择一次游戏"
        />
      </el-row>
      <el-row v-if="hasData">
        <h1 id="title">{{ title }}</h1>
      </el-row>
      <div style="display: inline-block" v-if="hasData">
        <el-row v-for="i in question" :key="i" id="titlediv">
          <p id="question">
            {{ i }}
          </p>
        </el-row>
      </div>
      <el-row v-if="hasData">
        <h3 id="ans">结果</h3>
      </el-row>
      <el-row v-if="hasData && gainScore != null && selected2">
        在这场游戏中，您选择了 {{ selected2 }}，{{
          gainScore >= 0 ? "获得" : "失去"
        }}了 {{ gainScore }} 分
      </el-row>
      <el-row v-if="hasData" id="ansPer">
        <div v-for="item in options" :key="item">
          <el-col style="margin-right: 10px">
            <div
              :style="
                item == selected2 ? { color: 'var(--el-color-primary)' } : ''
              "
            >
              {{ item }}
            </div>
          </el-col>
          <el-col>
            <el-progress
              :text-inside="true"
              :stroke-width="17"
              :percentage="
                participants.length == 0
                  ? 0
                  : Math.floor(
                      (allocations[options.indexOf(item)].length /
                        participants.length) *
                        1000
                    ) / 10
              "
              id="finishedAns"
            >
              <p style="margin: 0px">
                {{ allocations[options.indexOf(item)].length }}人，
                {{
                  participants.length == 0
                    ? 0
                    : Math.floor(
                        (allocations[options.indexOf(item)].length /
                          participants.length) *
                          1000
                      ) / 10
                }}%
              </p>
            </el-progress>
          </el-col>
        </div>
      </el-row>
    </el-col>
  </el-container>
</template>

<script>
import axios from "axios";
import { ElMessage, ElLoading } from "element-plus";
export default {
  name: "History",
  data() {
    return {
      activeName: "first",
      history: [
        {
          label: "123",
          value: 1,
        },
        {
          label: "234",
          value: 2,
        },
      ],
      props: {
        label: "label",
      },
      hasData: false,
      title: "",
      question: [],
      options: [],
      answer: null,
      endTime: 0,
      startTime: 0,
      allocations: [],
      participants: [],
      selected: null,
      loading: ElLoading.service({
        lock: true,
        text: "加载历史游戏列表中...",
        background: "rgba(255, 255, 255, 1)",
      }),
      selected2: null,
      gainScore: null,
    };
  },
  created() {
    this.getGameHistory();
  },
  methods: {
    getGameHistory() {
      axios
        .get("http://10.28.204.120:8000/games_titles")
        .then((res) => {
          if (res.data.status == "ok") {
            const games = res.data.games;
            this.history = [];
            for (let i = 0; i < games.length; i++) {
              this.history.push({
                label: i + ". " + games[i],
                value: i,
              });
            }
            this.history.reverse();
            setTimeout(() => {
              this.loading.close();
            }, 500);
          } else {
            ElMessage.error("获取历史游戏列表失败，请刷新重试");
            setTimeout(() => {
              this.loading.close();
            }, 500);
          }
        })
        .catch((err) => {
          console.log(err);
          ElMessage.error("获取历史游戏列表失败，请刷新重试");
          setTimeout(() => {
            this.loading.close();
          }, 500);
        });
    },
    startLoading() {
      this.loading = ElLoading.service({
        lock: true,
        text: "加载历史游戏列表中...",
        background: "rgba(255, 255, 255, 1)",
      });
    },
  },
  watch: {
    selected(val) {
      this.loading = ElLoading.service({
        lock: true,
        text: "加载历史游戏中...",
        background: "rgba(255, 255, 255, 1)",
      });
      console.log(val);
      let user_id = localStorage.getItem("user_id").replaceAll("#", "%23");

      console.log(user_id);
      if (val != null) {
        axios
          .get("http://10.28.204.120:8000/game/" + val + "/user/" + user_id)
          .then((res) => {
            if (res.data.status == "ok") {
              this.title = res.data.game.gid + ". " + res.data.game.title;
              this.question = res.data.game.question.split("\n");
              this.options = res.data.game.selections;
              this.startTime = res.data.game.start_timestamp_msec;
              this.endTime =
                res.data.game.start_timestamp_msec +
                res.data.game.duration_msec;
              this.allocations = res.data.game.allocations;
              this.participants = res.data.game.participants;
              this.hasData = true;
              this.selected2 =
                res.data.user_selection == -1
                  ? null
                  : this.options[res.data.user_selection];
              this.gainScore = res.data.result ? res.data.result : null;
              setTimeout(() => {
                this.loading.close();
              }, 500);
            } else if (
              res.data.status == "error" &&
              res.data.message == "game not found"
            ) {
              ElMessage.error("游戏不存在");
              setTimeout(() => {
                this.loading.close();
              }, 500);
            } else {
              ElMessage.error("获取游戏信息失败，请刷新重试");
              setTimeout(() => {
                this.loading.close();
              }, 500);
            }
          })
          .catch((err) => {
            console.log(err);
            ElMessage.error("获取游戏信息失败，请刷新重试");
            setTimeout(() => {
              this.loading.close();
            }, 500);
          });
      }
    },
  },
};
</script>

<style scoped>
.el-row {
  max-width: 600px;
  place-content: center;
  margin-bottom: 20px;
}
.el-radio {
  margin-top: 10px;
  margin-left: 10px;
  margin-right: 10px;
}
#select-place {
  justify-content: center;
  max-width: 400px;
  margin-top: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fill, 170px);
  width: 100%;
}
.el-radio:last-child {
  margin-right: 10px !important;
}
.el-radio__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#titlediv {
  place-content: unset;
  text-align: left;
}
.el-button {
  margin-top: 20px;
}
.demo-progress .el-progress--line {
  margin-bottom: 15px;
  width: 350px;
}
.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 28px;
}
.percentage-label {
  display: block;
  margin-top: 10px;
  font-size: 12px;
}
#finishedAns {
  margin-bottom: 15px;
  width: 250px;
}
#title {
  margin: 0px;
}
#status {
  margin: 0px;
}
#question {
  margin: 0px;
}
#ans {
  margin-top: 80px;
}
#container {
  padding: 30px;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  text-align: -webkit-center;
  text-align: -moz-center;
}
#ansPer {
  max-width: 400px;
}
</style>