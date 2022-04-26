<template>
  <el-container id="container">
    <el-col>
      <el-row>
        你是 {{ user_id }}，<el-link type="primary" @click="remake"
          >Remake</el-link
        >
      </el-row>
      <el-row>
        <h1 id="title">{{ title }}</h1>
      </el-row>
      <el-row v-if="status == 'finished'">
        <p style="color: gray" id="status">游戏已结束</p>
      </el-row>
      <el-row v-if="status == 'waiting'">
        <p style="color: gray" id="status">游戏尚未开始</p>
      </el-row>
      <el-row v-if="status == 'started' || status == 'waiting'">
        <div class="demo-progress">
          <el-progress
            type="dashboard"
            :percentage="endPercent"
            :countDown="countDown"
          >
            <template #default="{}">
              <span class="percentage-value">{{ countDown }}</span>
              <span class="percentage-label">剩余时间</span>
            </template>
          </el-progress>
        </div>
      </el-row>
      <div style="display: inline-block">
        <el-row v-for="i in question" :key="i" id="titlediv">
          <p id="question">
            {{ i }}
          </p>
        </el-row>
      </div>
      <el-row v-if="status == 'started'">
        <div>
          <el-radio-group v-model="answer">
            <div id="select-place">
              <el-radio
                :label="item"
                size="large"
                border
                v-for="item in options"
                :key="item"
                >{{ item }}
              </el-radio>
            </div>
          </el-radio-group>
        </div>
      </el-row>
      <el-row v-if="status == 'started'">
        <el-button type="primary" size="large" @click="submitAns">
          提交答案
        </el-button>
      </el-row>
      <el-row v-if="status == 'finished'">
        <h3 id="ans">结果</h3>
      </el-row>
      <el-row v-if="status == 'finished'" id="ansPer">
        <div v-for="item in options" :key="item">
          <el-col style="margin-right: 10px">
            <div>
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
import { ElMessage, ElLoading, ElMessageBox } from "element-plus";
export default {
  name: "Game",
  data() {
    return {
      title: "",
      question: [],
      options: [],
      answer: null,
      endTime: 0,
      startTime: 0,
      countDown: "",
      endPercent: 0,
      loading: ElLoading.service({
        lock: true,
        text: "加载题目中...",
        background: "rgba(255, 255, 255, 1)",
      }),
      loading2: ElLoading.service({
        lock: true,
        text: "获取昵称中...",
        background: "rgba(255, 255, 255, 1)",
      }),
      status: "",
      allocations: [],
      participants: [],
    };
  },
  created() {
    this.setUserID();
    this.updateCountDown();
    this.getTitle();
  },
  methods: {
    updateCountDown() {
      let now = Date.now();
      if (now > this.endTime && this.status == "started") {
        location.reload();
        return;
      }
      if (now > this.startTime && this.status == "waiting") {
        location.reload();
        return;
      }
      if (this.status == "started") {
        let hour = Math.floor((this.endTime - now) / (1000 * 60 * 60));
        let minute = Math.floor((this.endTime - now) / (1000 * 60)) % 60;
        let second = Math.floor((this.endTime - now) / 1000) % 60;
        if (minute < 10) {
          minute = "0" + minute;
        }
        if (second < 10) {
          second = "0" + second;
        }
        this.countDown = `${hour}:${minute}:${second}`;
        this.endPercent =
          Math.floor(
            ((now - this.startTime) / (this.endTime - this.startTime)) * 1000
          ) / 10;
      } else if (this.status == "waiting") {
        let hour = Math.floor((this.startTime - now) / (1000 * 60 * 60));
        let minute = Math.floor((this.startTime - now) / (1000 * 60)) % 60;
        let second = Math.floor((this.startTime - now) / 1000) % 60;
        if (minute < 10) {
          minute = "0" + minute;
        }
        if (second < 10) {
          second = "0" + second;
        }
        this.countDown = `${hour}:${minute}:${second}`;
        this.endPercent = 0;
      }

      setTimeout(this.updateCountDown, 1000);
    },
    submitAns() {
      const data = {
        selection: this.options.indexOf(this.answer),
        timestamp: Date.now(),
        user_id: this.user_id,
        game_id: this.game_id,
      };
      axios
        .post("http://81.70.254.227:8000/submits", data)
        .then((res) => {
          if (res.data.status === "ok") {
            ElMessage.success("提交成功");
          } else if (res.data.status === "duplicate") {
            ElMessage.error("你已经提交过了");
          } else {
            ElMessage.error("提交失败, " + res.data.status);
          }
        })
        .catch((err) => {
          ElMessage.error("提交失败, " + err);
        });
    },
    async getTitle() {
      axios
        .get("http://81.70.254.227:8000/submits")
        .then((res) => {
          try {
            this.title = res.data.title;
            this.question = res.data.question.split("\n");
            this.options = res.data.selections;
            this.startTime = res.data.start_timestamp_msec;
            this.endTime =
              res.data.start_timestamp_msec + res.data.duration_msec;
            this.updateCountDown();
            this.status = res.data.status;
            this.allocations = res.data.allocations;
            this.participants = res.data.participants;
            this.game_id = res.data.gid;
            if (Date.now() < this.startTime) {
              this.status = "waiting";
            }
            setTimeout(() => {
              this.loading.close();
            }, 500);
          } catch (e) {
            console.log(e);
            ElMessage.error("获取题目失败");
          }
        })
        .catch((err) => {
          console.log(err);
          ElMessage.error("获取题目失败");
        });
    },
    setUserID() {
      if (localStorage.getItem("user_id")) {
        this.user_id = localStorage.getItem("user_id");
      } else {
        axios
          .get("http://81.70.254.227:8000/rand_username")
          .then((res) => {
            if (res.data.status == "ok") {
              localStorage.setItem("user_id", res.data.username);
              this.user_id = res.data.username;
              setTimeout(() => {
                this.loading2.close();
              }, 500);
            } else {
              console.log(res.data.message);
              ElMessage.error("获取用户ID失败，重试");
              setTimeout(() => {
                this.setUserID();
              }, 1000);
            }
          })
          .catch((err) => {
            console.log(err);
            ElMessage.error("获取用户ID失败，重试");
            setTimeout(() => {
              this.setUserID();
            }, 1000);
          });
      }
    },
    remake() {
      ElMessageBox.confirm("这样做会清空您的所有数据，继续吗？", "警告", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          localStorage.removeItem("user_id");
          location.reload();
        })
        .catch(() => {
          ElMessage({
            type: "success",
            message: "恭喜你，请不要放弃自己。",
          });
        });
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
}
#ansPer {
  max-width: 400px;
}
</style>
