import axios from 'axios'

let _api = null

const api = () => {
  if (!_api) {
    _api = axios.create({
      baseURL: '/api/v1',
      withCredentials: false,
      headers: {
        'Accecpt': 'application/json',
        'Content-Type': 'application/json'
      },
      responseType: 'json'
    })
  }
  return _api
}

export { api }
