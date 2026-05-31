import Dashboard from '../views/Dashboard.vue'
import FileDetail from '../views/FileDetail.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: Dashboard,
    children: [
      {
        path: 'file/:filename',
        name: 'file-detail',
        component: FileDetail,
        props: true
      }
    ]
  }
]

export default routes
