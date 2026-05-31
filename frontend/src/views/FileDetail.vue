<template>
  <DiffViewer
    :file="selectedFile"
    :diff-data="diffData"
    :review-data="reviewData"
  />
</template>

<script>
import { computed } from 'vue'
import DiffViewer from '../components/DiffViewer.vue'

export default {
  name: 'FileDetail',
  components: { DiffViewer },
  props: {
    diffData: { type: Object, default: null },
    reviewData: { type: Object, default: null },
    activeFile: { type: String, default: null }
  },
  setup(props) {
    const selectedFile = computed(() => {
      if (!props.diffData?.structured_diff?.files || !props.activeFile) return null
      return props.diffData.structured_diff.files.find(f => f.filename === props.activeFile) || null
    })
    return { selectedFile }
  }
}
</script>
