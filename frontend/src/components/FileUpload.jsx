import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, X, File } from 'lucide-react'

const fileTypeIcons = {
  pdf: '📄',
  docx: '📝',
  txt: '📃',
}

export default function FileUpload({ files, setFiles, onGenerate, isLoading }) {
  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prev) => [...prev, ...acceptedFiles])
  }, [setFiles])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
  })

  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx))
  }

  return (
    <div className="space-y-6">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
          isDragActive
            ? 'border-primary-400 bg-primary-500/10'
            : 'border-white/20 hover:border-white/40 hover:bg-white/5'
        }`}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={isDragActive ? { scale: 1.05 } : { scale: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <div className="w-16 h-16 bg-primary-600/20 rounded-2xl flex items-center justify-center border border-primary-500/30">
            <Upload className="w-8 h-8 text-primary-400" />
          </div>
          <div>
            <p className="text-lg font-medium text-white">
              {isDragActive ? 'Drop files here' : 'Drag & drop documents'}
            </p>
            <p className="text-sm text-white/40 mt-1">
              Supports PDF, DOCX, and TXT files
            </p>
          </div>
        </motion.div>
      </div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="space-y-3"
          >
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
              Uploaded Documents ({files.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {files.map((file, idx) => {
                const ext = file.name.split('.').pop().toLowerCase()
                return (
                  <motion.div
                    key={`${file.name}-${idx}`}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="glass-card p-4 flex items-center gap-3"
                  >
                    <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center text-lg">
                      {fileTypeIcons[ext] || '📄'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{file.name}</p>
                      <p className="text-xs text-white/40">
                        {(file.size / 1024).toFixed(1)} KB · {ext.toUpperCase()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); removeFile(idx) }}
                      className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                    >
                      <X className="w-4 h-4 text-white/40" />
                    </button>
                  </motion.div>
                )
              })}
            </div>

            {/* Generate Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onGenerate}
              disabled={isLoading}
              className="btn-primary w-full mt-4 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing Documents...
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  Generate Memory
                </>
              )}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
