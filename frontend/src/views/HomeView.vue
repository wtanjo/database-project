<template>
  <div class="container">
    <h1>Web Crawler MVP</h1>

    <!-- 输入区 -->
    <div class="search-bar">
      <el-input 
        v-model="crawlUrl" 
        placeholder="请输入要爬取的 URL (例如 https://quotes.toscrape.com/)" 
        clearable
        style="width: 400px; margin-right: 10px;"
      />
      <el-button type="primary" :loading="loading" @click="handleStartCrawl">
        开始爬取
      </el-button>
      <el-button @click="fetchData">刷新列表</el-button>
    </div>

    <!-- 结果展示区 -->
    <el-table :data="tableData" border style="width: 100%; margin-top: 20px" v-loading="tableLoading">
      <el-table-column prop="_id" label="ID" width="220" />
      <el-table-column prop="webpage_url" label="来源 URL" width="250" show-overflow-tooltip />
      <el-table-column prop="title" label="网页标题" width="200" />
      <el-table-column prop="text_content" label="正文预览" show-overflow-tooltip />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createTask, getContents } from '../api/task'

const crawlUrl = ref('')
const loading = ref(false)
const tableLoading = ref(false)
const tableData = ref([])

// 提交爬取任务
const handleStartCrawl = async () => {
  if (!crawlUrl.value) {
    return ElMessage.warning('请输入URL')
  }
  
  loading.value = true
  try {
    const res = await createTask(crawlUrl.value)
    if (res.data.status === 'success') {
      ElMessage.success(`任务已启动，ID: ${res.data.task_id}`)
      // 延迟3秒后自动刷新一次列表
      setTimeout(fetchData, 3000)
    }
  } catch (error: any) {
    const msg = error?.response?.data?.detail || error?.message || '未知错误'
    ElMessage.error(`触发失败: ${msg}`)
    console.error('createTask error:', error)
  } finally {
    loading.value = false
  }
}

// 获取列表数据
const fetchData = async () => {
  tableLoading.value = true
  try {
    const res = await getContents()
    tableData.value = res.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    tableLoading.value = false
  }
}

// 页面加载时自动拉取一次数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.container {
  padding: 40px;
  max-width: 1000px;
  margin: 0 auto;
}
.search-bar {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}
</style>