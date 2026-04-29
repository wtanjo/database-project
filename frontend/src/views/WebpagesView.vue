<template>
  <div>
    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="域名">
          <el-input v-model="searchDomain" placeholder="域名关键字" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="searchUrl" placeholder="URL 关键字" clearable style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 网页列表 -->
    <el-card shadow="never">
      <el-table
        :data="webpages"
        v-loading="loading"
        border
        stripe
        @row-click="handleRowClick"
        row-class-name="clickable-row"
      >
        <el-table-column prop="id" label="ID" width="65" align="center" />
        <el-table-column prop="domain" label="域名" width="180" show-overflow-tooltip />
        <el-table-column prop="title" label="标题" width="180" show-overflow-tooltip />
        <el-table-column prop="url" label="URL" show-overflow-tooltip min-width="200" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="爬取时间" width="170">
          <template #default="{ row }">
            {{ row.crawl_time ? new Date(row.crawl_time).toLocaleString('zh-CN') : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ row }">
            <el-popconfirm
              title="删除该网页及其内容和图片？"
              @confirm="handleDelete(row.id)"
              width="200"
            >
              <template #reference>
                <el-button size="small" type="danger" :icon="Delete" circle @click.stop />
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchWebpages"
      />
    </el-card>

    <!-- 网页详情抽屉 -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="52%" direction="rtl">
      <div v-loading="detailLoading" class="drawer-body">
        <template v-if="detail">
          <!-- 基本信息 + 跳转按钮 -->
          <el-descriptions :column="1" border size="small" style="margin-bottom: 12px">
            <el-descriptions-item label="URL">
              <a :href="detail.url" target="_blank" class="url-link">{{ detail.url }}</a>
            </el-descriptions-item>
            <el-descriptions-item label="爬取时间">{{ detail.crawl_time }}</el-descriptions-item>
          </el-descriptions>

          <!-- 跳转操作区 -->
          <div class="jump-bar">
            <span class="jump-label">在以下页面中查看：</span>
            <el-button size="small" type="primary" plain :icon="Document" @click="goContents">
              内容检索
            </el-button>
            <el-button size="small" type="success" plain :icon="Picture" @click="goImages">
              图片管理
            </el-button>
          </div>

          <!-- 正文检索 -->
          <el-divider content-position="left">正文内容</el-divider>
          <template v-if="detail.content">
            <!-- 关键词标签 -->
            <div v-if="detail.content.keywords?.length" style="margin-bottom: 10px">
              <el-tag
                v-for="kw in detail.content.keywords"
                :key="kw"
                size="small"
                style="margin-right: 4px; cursor: pointer"
                @click="contentSearch = kw"
              >{{ kw }}</el-tag>
            </div>

            <!-- 正文内搜索框 -->
            <el-input
              v-model="contentSearch"
              placeholder="在正文中搜索..."
              clearable
              :prefix-icon="Search"
              style="margin-bottom: 10px"
            >
              <template #append>
                <span class="match-count" v-if="contentSearch">
                  {{ matchCount }} 处匹配
                </span>
              </template>
            </el-input>

            <!-- 正文（高亮显示匹配词） -->
            <el-scrollbar height="320px" class="content-scrollbar">
              <div class="text-content" v-html="highlightedText" />
            </el-scrollbar>
          </template>
          <el-empty v-else description="未爬取到正文" :image-size="48" />

          <!-- 图片 -->
          <el-divider content-position="left">图片（{{ detail.images?.length ?? 0 }} 张）</el-divider>
          <template v-if="detail.images?.length">
            <div class="image-grid">
              <div v-for="(img, i) in detail.images" :key="i" class="image-cell">
                <el-image
                  :src="img.image_url"
                  fit="cover"
                  class="thumb"
                  :preview-src-list="detail.images.map((d: any) => d.image_url)"
                  :initial-index="i"
                  lazy
                >
                  <template #error>
                    <div class="thumb-error"><el-icon><Picture /></el-icon></div>
                  </template>
                </el-image>
                <div class="thumb-desc">{{ img.description || '—' }}</div>
              </div>
            </div>
          </template>
          <el-empty v-else description="未爬取到图片" :image-size="48" />
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Search, Picture, Document } from '@element-plus/icons-vue'
import { getWebpages, getWebpageDetail, deleteWebpage } from '@/api/index'

const router = useRouter()

const route = useRoute()

// ── Search ────────────────────────────────────────────────────────────────────
const searchDomain = ref((route.query.domain as string) || '')
const searchUrl = ref('')

// ── Webpages ──────────────────────────────────────────────────────────────────
const webpages = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function fetchWebpages() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchDomain.value) params.domain = searchDomain.value
    if (searchUrl.value) params.url_keyword = searchUrl.value
    const res: any = await getWebpages(params)
    if (res.code === 0) {
      webpages.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchWebpages()
}

function handleReset() {
  searchDomain.value = ''
  searchUrl.value = ''
  page.value = 1
  fetchWebpages()
}

async function handleDelete(id: number) {
  try {
    const res: any = await deleteWebpage(id)
    if (res.code === 0) {
      ElMessage.success('删除成功')
      fetchWebpages()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch {
    ElMessage.error('请求失败')
  }
}

function statusType(status: string) {
  const map: Record<string, string> = { success: 'success', failed: 'danger', pending: 'info', fetching: 'warning' }
  return map[status] ?? ''
}

// ── Detail Drawer ─────────────────────────────────────────────────────────────
const drawerVisible = ref(false)
const drawerTitle = ref('')
const detailLoading = ref(false)
const detail = ref<any>(null)
const contentSearch = ref('')

async function handleRowClick(row: any) {
  drawerTitle.value = row.title || row.url
  drawerVisible.value = true
  contentSearch.value = ''
  detail.value = null
  detailLoading.value = true
  try {
    const res: any = await getWebpageDetail(row.id)
    if (res.code === 0) detail.value = res.data
  } finally {
    detailLoading.value = false
  }
}

// 正文高亮：将 contentSearch 关键字用 <mark> 包裹
const highlightedText = computed(() => {
  const raw = detail.value?.content?.text_content ?? ''
  if (!contentSearch.value.trim()) return escapeHtml(raw)
  const keyword = escapeHtml(contentSearch.value.trim())
  const escaped = escapeHtml(raw)
  const regex = new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
  return escaped.replace(regex, (m) => `<mark class="highlight">${m}</mark>`)
})

const matchCount = computed(() => {
  if (!contentSearch.value.trim() || !detail.value?.content?.text_content) return 0
  const regex = new RegExp(contentSearch.value.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
  return (detail.value.content.text_content.match(regex) ?? []).length
})

function escapeHtml(str: string) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br/>')
}

function goContents() {
  router.push({ path: '/contents', query: { webpage_url: detail.value?.url } })
  drawerVisible.value = false
}

function goImages() {
  router.push({ path: '/images', query: { webpage_url: detail.value?.url } })
  drawerVisible.value = false
}

// 从网站管理页带 domain 参数跳转过来时自动触发搜索
watch(() => route.query.domain, (val) => {
  if (val) {
    searchDomain.value = val as string
    page.value = 1
    fetchWebpages()
  }
})

onMounted(fetchWebpages)
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}
.search-card :deep(.el-card__body) {
  padding: 16px 20px 8px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover td) { background-color: #ecf5ff !important; }

.drawer-body { padding: 0 4px; }
.url-link { color: #409eff; word-break: break-all; }
.jump-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 10px 12px;
  background: #f7f4ef;
  border-radius: 8px;
  border: 1px solid #ede9e3;
}
.jump-label {
  font-size: 12px;
  color: #8a8080;
  margin-right: 4px;
}

.content-scrollbar {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px 14px;
  background: #fafafa;
}
.text-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  word-break: break-word;
}
:deep(.highlight) {
  background-color: #ffe58f;
  color: #333;
  border-radius: 2px;
  padding: 0 2px;
}
.match-count {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
}
.image-cell { display: flex; flex-direction: column; gap: 4px; }
.thumb { width: 100%; height: 85px; border-radius: 4px; }
.thumb-error {
  width: 100%; height: 85px;
  display: flex; align-items: center; justify-content: center;
  background: #f5f7fa; color: #c0c4cc;
}
.thumb-desc {
  font-size: 11px; color: #909399;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
</style>
