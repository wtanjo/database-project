<template>
  <div>
    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键字">
          <el-input v-model="keyword" placeholder="正文关键字" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Download" @click="handleExport">导出 CSV</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果列表 -->
    <div v-loading="loading">
      <el-empty v-if="!loading && items.length === 0" description="暂无数据" />

      <el-card
        v-for="item in items"
        :key="item.webpage_id ?? item.url"
        shadow="hover"
        class="content-card"
      >
        <div class="content-header">
          <div class="content-title">{{ item.title || '（无标题）' }}</div>
          <el-tag size="small" type="info">{{ item.crawl_time }}</el-tag>
        </div>
        <a :href="item.url" target="_blank" class="content-url">{{ item.url }}</a>
        <p class="content-text">{{ truncate(item.text_content, 200) }}</p>

        <!-- 关键词 -->
        <div v-if="item.keywords?.length" class="tags">
          <el-tag
            v-for="kw in item.keywords"
            :key="kw"
            size="small"
            style="margin-right: 4px"
          >{{ kw }}</el-tag>
        </div>

        <!-- 图片缩略图 -->
        <div v-if="item.images?.length" class="thumbs">
          <el-image
            v-for="(img, i) in item.images.slice(0, 5)"
            :key="i"
            :src="img"
            fit="cover"
            class="thumb"
            :preview-src-list="item.images"
            :initial-index="i"
            lazy
          />
        </div>
      </el-card>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchContents"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { getContents, exportContentsCSV } from '@/api/index'

const keyword = ref('')
const dateRange = ref<[string, string] | null>(null)
const loading = ref(false)
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

async function fetchContents() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (dateRange.value) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const res: any = await getContents(params)
    if (res.code === 0) {
      items.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchContents()
}

function handleReset() {
  keyword.value = ''
  dateRange.value = null
  page.value = 1
  fetchContents()
}

function handleExport() {
  exportContentsCSV({
    keyword: keyword.value || undefined,
    start_time: dateRange.value?.[0],
    end_time: dateRange.value?.[1],
  })
}

function truncate(text: string, len: number) {
  if (!text) return ''
  return text.length > len ? text.slice(0, len) + '...' : text
}

onMounted(fetchContents)
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}
.search-card :deep(.el-card__body) {
  padding: 16px 20px 8px;
}
.content-card {
  margin-bottom: 12px;
  border-radius: 8px;
}
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.content-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.content-url {
  font-size: 12px;
  color: #409eff;
  word-break: break-all;
}
.content-text {
  font-size: 13px;
  color: #606266;
  margin: 8px 0;
  line-height: 1.6;
}
.tags {
  margin-bottom: 8px;
}
.thumbs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.thumb {
  width: 80px;
  height: 60px;
  border-radius: 4px;
  object-fit: cover;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
