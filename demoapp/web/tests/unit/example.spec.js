import { shallowMount } from '@vue/test-utils'
import TodoList from '@/components/TodoList.vue'

describe('TodoList.vue', () => {
  it('renders props.title when passed', () => {
    const title = 'new message'
    const wrapper = shallowMount(TodoList, {
      propsData: { title }
    })
    console.log('|', wrapper.text(), '|')
    expect(wrapper.text()).toMatch(title)
  })
})
