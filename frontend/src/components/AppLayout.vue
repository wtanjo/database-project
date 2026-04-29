<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="aside">
      <div class="logo">
        <span>爬虫管理系统</span>
      </div>
      <el-menu
        :default-active="activeRoute"
        router
        background-color="#1a1a2e"
        text-color="#c0c4cc"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>爬取管理</span>
        </el-menu-item>
        <el-menu-item index="/contents">
          <el-icon><Search /></el-icon>
          <span>内容检索</span>
        </el-menu-item>
        <el-menu-item index="/images">
          <el-icon><Picture /></el-icon>
          <span>图片管理</span>
        </el-menu-item>
        <el-menu-item index="/websites">
          <el-icon><Monitor /></el-icon>
          <span>网站管理</span>
        </el-menu-item>
        <el-menu-item index="/webpages">
          <el-icon><Link /></el-icon>
          <span>网页管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <span class="header-title">{{ pageTitle }}</span>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, List, Search, Picture, Monitor, Link } from '@element-plus/icons-vue'

const route = useRoute()
const activeRoute = computed(() => route.path)

const titleMap: Record<string, string> = {
  '/': '仪表盘',
  '/tasks': '爬取管理',
  '/contents': '内容检索',
  '/images': '图片管理',
  '/websites': '网站管理',
  '/webpages': '网页管理',
}
const pageTitle = computed(() => titleMap[route.path] || '爬虫管理系统')
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.aside {
  background-color: #1a1a2e;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #2a2a4a;
  background-color: #16213e;
  letter-spacing: 1px;
}

.el-menu {
  border-right: none;
  flex: 1;
}

.header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.main {
  background: #f5f7fa;
  overflow-y: auto;
  padding: 24px;
}
</style>
