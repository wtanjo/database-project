import service from './request'; // 引入你截图中的 axios 实例

// 定义请求参数的接口
interface CreateTaskData {
  url: string;
}

// 封装调用函数
export function createTask(data: CreateTaskData) {
  return service({
    url: '/tasks', // 注意：baseURL 已经是 /api 了，这里只需写 /tasks
    method: 'post',
    data: data // 对应后端的 url_data
  });
}