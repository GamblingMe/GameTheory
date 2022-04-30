<template>
  <el-container id="container">
    <el-table
      :data="rankList"
      style="width: 100%"
      :row-class-name="tableRowClassName"
    >
      <el-table-column prop="rank" label="排名" width="80" />
      <el-table-column prop="name" label="昵称" width="160" />
      <el-table-column prop="point" label="积分" width="120" />
    </el-table>
  </el-container>
  <el-button type="primary" class="fixed-button" @click="goToMe">
    <el-icon class="el-icon--left">
      <Sort />
    </el-icon>
    我的
  </el-button>
</template>

<script>
import axios from "axios";
import { ElMessage, ElLoading } from "element-plus";
export default {
  name: "Rank",
  data() {
    return {
      rankList: [
        { name: "老虎#113", point: 20, rank: 1 },
        { name: "猴子#22", point: 10, rank: 2 },
      ],
      loading: ElLoading.service({
        lock: true,
        text: "加载排行榜中...",
        background: "rgba(255, 255, 255, 1)",
      }),
    };
  },
  created() {
    this.getRankList();
  },
  methods: {
    getRankList() {
      axios
        .get("http://10.28.204.120:8000/rank")
        .then((res) => {
          if (res.data.status == "ok") {
            let rank = res.data.rank;
            const maxRank = 3;
            const myName = localStorage.getItem("user_id");
            let tmpRankList = [];
            this.rankList = [];
            console.log(rank);
            for (let i in rank) {
              tmpRankList.push({
                name: i,
                point: rank[i],
              });
            }
            tmpRankList.sort((a, b) => {
              return b.point - a.point;
            });
            let flag = false;
            for (let i in tmpRankList) {
              if (tmpRankList[i].name == myName) {
                flag = i;
              }
              tmpRankList[i].rank = parseInt(i) + 1;
              if (parseInt(i) + 1 <= maxRank) {
                this.rankList.push(tmpRankList[i]);
              }
            }
            if (flag >= maxRank) {
              this.rankList.push({
                name: "...",
                point: "...",
                rank: "...",
              });
              this.rankList.push({
                name: myName,
                point: rank[myName],
                rank: maxRank + "+",
              });
            }
            setTimeout(() => {
              this.loading.close();
            }, 500);
          } else {
            ElMessage.error("获取排名失败，请刷新重试");
            setTimeout(() => {
              this.loading.close();
            }, 500);
          }
        })
        .catch((err) => {
          console.log(err);
          ElMessage.error("获取排名失败，请刷新重试");
          setTimeout(() => {
            this.loading.close();
          }, 500);
        });
    },
    tableRowClassName({ row }) {
      if (localStorage.getItem("user_id") == row.name) {
        return "my-row";
      }
    },
    goToMe() {
      // smooth
      document.getElementsByClassName("my-row")[0].scrollIntoView({
        behavior: "smooth",
      });
    },
    startLoading() {
      this.loading = ElLoading.service({
        lock: true,
        text: "加载排行榜中...",
        background: "rgba(255, 255, 255, 1)",
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
  padding: 8px 8px;
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
.fixed-button {
  position: fixed;
  bottom: 20px;
  z-index: 999;
  right: 20px;
}
</style>

<style>
.el-table__row.my-row {
  background-color: var(--el-color-success-light-9);
}
</style>