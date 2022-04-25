<template>
  <el-container id="container">
    <el-table :data="rankList" stripe style="width: 100%">
      <el-table-column prop="rank" label="排名" width="120" />
      <el-table-column prop="name" label="昵称" width="120" />
      <el-table-column prop="point" label="积分" width="120" />
    </el-table>
  </el-container>
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
        .get("http://81.70.254.227:8000/rank")
        .then((res) => {
          if (res.data.status == "ok") {
            let rank = res.data.rank;
            this.rankList = [];
            console.log(rank);
            for (let i in rank) {
              this.rankList.push({
                name: i,
                point: rank[i],
              });
            }
            this.rankList.sort((a, b) => {
              return b.point - a.point;
            });
            for (let i in this.rankList) {
              this.rankList[i].rank = parseInt(i) + 1;
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