<template>
  <div>
    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="描述关键字">
          <el-input v-model="keyword" placeholder="图片描述关键字" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="来源页面">
          <el-input v-model="webpageUrl" placeholder="URL 关键字" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="爬取时间">
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
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图片网格 -->
    <div v-loading="loading">
      <el-empty v-if="!loading && images.length === 0" description="暂无图片" />

      <div class="image-grid">
        <div v-for="img in images" :key="img.id" class="image-card">
          <el-image
            :src="img.image_url"
            fit="cover"
            class="image-item"
            :preview-src-list="previewList"
            :initial-index="images.indexOf(img)"
            lazy
          >
            <template #error>
              <div class="image-error">
                <el-icon :size="24" color="#c0c4cc"><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div class="image-meta">
            <el-tooltip :content="img.description || '无描述'" placement="top">
              <div class="image-desc">{{ img.description || '无描述' }}</div>
            </el-tooltip>
            <div class="image-url">
              <a :href="img.webpage_url" target="_blank" class="link">来源页面</a>
            </div>
          </div>
        </div>
      </div>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 40, 80]"
        layout="total, sizes, prev, pager, next"
        @change="fetchImages"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { getImages } from '@/api/index'

const route = useRoute()
const keyword = ref('')
const webpageUrl = ref((route.query.webpage_url as string) || '')
const dateRange = ref<[string, string] | null>(null)
const loading = ref(false)
const images = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const previewList = computed(() => images.value.map((img) => img.image_url))

async function fetchImages() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (webpageUrl.value) params.webpage_url = webpageUrl.value
    if (dateRange.value) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const res: any = await getImages(params)
    if (res.code === 0) {
      images.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchImages()
}

function handleReset() {
  keyword.value = ''
  webpageUrl.value = ''
  dateRange.value = null
  page.value = 1
  fetchImages()
}

watch(() => route.query.webpage_url, (val) => {
  if (val) {
    webpageUrl.value = val as string
    page.value = 1
    fetchImages()
  }
})

onMounted(fetchImages)
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}
.search-card :deep(.el-card__body) {
  padding: 16px 20px 8px;
}
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.image-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s;
}
.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.image-item {
  width: 100%;
  height: 140px;
  display: block;
}
.image-error {
  width: 100%;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.image-meta {
  padding: 8px 10px;
}
.image-desc {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.image-url {
  margin-top: 4px;
}
.link {
  font-size: 11px;
  color: #409eff;
}
.pagination {
  justify-content: flex-end;
}
</style>
