<template>
  <el-tabs
    v-model="activeName"
    type="card"
    class="demo-tabs"
    @tab-click="handleClick"
  >
    <el-tab-pane label="游戏" name="first">
      <Game />
    </el-tab-pane>
    <el-tab-pane label="历史" name="second">
      <History />
    </el-tab-pane>
    <el-tab-pane label="排行榜" name="third">
      <Rank />
    </el-tab-pane>
  </el-tabs>
  <el-footer>
    <div>V0.2.3</div>
    <el-link href="https://github.com/GamblingMe/GamblingNow/" type="primary"
      >Powered by GameTheory</el-link
    >
  </el-footer>
</template>

<script>
import Game from "./components/Game.vue";
import History from "./components/History.vue";
import Rank from "./components/Rank.vue";
export default {
  name: "App",
  components: {
    Game,
    History,
    Rank,
  },
  data() {
    return {
      activeName: "first",
    };
  },
  methods: {
    handleClick(tab) {
      console.log(tab);
      if (tab.paneName == "first") {
        Game.methods.startLoading();
        Game.methods.setUserID();
        Game.methods.updateCountDown();
      } else if (tab.paneName == "second") {
        History.methods.startLoading();
        History.methods.getGameHistory();
      } else if (tab.paneName == "third") {
        Rank.methods.startLoading();
        Rank.methods.getRankList();
      }
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  text-align: -webkit-center;
  text-align: -moz-center;
}
.el-footer {
  margin-top: 50px;
}
.el-message-box {
  max-width: 90%;
}
</style>
