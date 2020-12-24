import { api } from '@/services/api'

const rootPath = '/task/'

export default {
  list() {
    return api().get(rootPath)
  },
  create(data) {
    return api().post(rootPath, data)
  },
  toggle(pk, is_done) {
    return api().patch(`${rootPath}${pk}/`, {is_done: is_done})
  },
  delete(pk) {
    return api().delete(`${rootPath}${pk}/`)
  }
}
