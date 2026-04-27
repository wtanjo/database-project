<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>数据采集管理系统</h1>
      </el-header>
      <el-main>
        <el-card>
          <template #header>爬虫任务控制</template>
          <el-button type="success" @click="startTask">启动 Scrapy 任务</el-button>
          <el-button type="danger">停止任务</el-button>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

const startTask = () => {
  ElMessage.success('任务已指令发送至 FastAPI 后端！')
}
</script>

<style scoped>
.home { padding: 20px; }
.el-header { background: #409EFF; color: white; line-height: 60px; }
</style>