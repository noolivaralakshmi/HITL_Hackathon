import { useState } from 'react'
import { motion } from 'framer-motion'
import { Save, X, Plus, Trash2, FileText } from 'lucide-react'

export default function EditableReasoningRecord({ reasoning, onSave, onCancel }) {
  const [edited, setEdited] = useState(JSON.parse(JSON.stringify(reasoning || {})))

  const updateField = (key, value) => {
    setEdited(prev => ({ ...prev, [key]: value }))
  }

  const updateListItem = (key, index, value) => {
    setEdited(prev => {
      const list = [...(prev[key] || [])]
      list[index] = value
      return { ...prev, [key]: list }
    })
  }

  const addListItem = (key, defaultValue = '') => {
    setEdited(prev => ({
      ...prev,
      [key]: [...(prev[key] || []), defaultValue]
    }))
  }

  const removeListItem = (key, index) => {
    setEdited(prev => ({
      ...prev,
      [key]: (prev[key] || []).filter((_, i) => i !== index)
    }))
  }

  const updateAltField = (index, field, value) => {
    setEdited(prev => {
      const alts = [...(prev.alternatives_considered || [])]
      alts[index] = { ...alts[index], [field]: value }
      return { ...prev, alternatives_considered: alts }
    })
  }

  const addAlternative = () => {
    setEdited(prev => ({
      ...prev,
      alternatives_considered: [...(prev.alternatives_considered || []), { name: '', rejected_reason: '' }]
    }))
  }

  const removeAlternative = (index) => {
    setEdited(prev => ({
      ...prev,
      alternatives_considered: (prev.alternatives_considered || []).filter((_, i) => i !== index)
    }))
  }

  const renderStringField = (key, label) => (
    <div key={key} className="space-y-2">
      <label className="text-sm font-medium text-white/60 uppercase tracking-wider">{label}</label>
      <textarea
        value={edited[key] || ''}
        onChange={(e) => updateField(key, e.target.value)}
        className="input-field text-sm min-h-[60px] resize-y"
        rows={2}
      />
    </div>
  )

  const renderListField = (key, label) => (
    <div key={key} className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-white/60 uppercase tracking-wider">{label}</label>
        <button
          onClick={() => addListItem(key, '')}
          className="text-xs flex items-center gap-1 text-primary-400 hover:text-primary-300"
        >
          <Plus className="w-3 h-3" /> Add
        </button>
      </div>
      {(edited[key] || []).map((item, idx) => (
        <div key={idx} className="flex items-center gap-2">
          <input
            type="text"
            value={typeof item === 'string' ? item : JSON.stringify(item)}
            onChange={(e) => updateListItem(key, idx, e.target.value)}
            className="input-field text-sm flex-1 py-2"
          />
          <button
            onClick={() => removeListItem(key, idx)}
            className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  )

  const renderAlternatives = () => (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-white/60 uppercase tracking-wider">Alternatives Considered</label>
        <button
          onClick={addAlternative}
          className="text-xs flex items-center gap-1 text-primary-400 hover:text-primary-300"
        >
          <Plus className="w-3 h-3" /> Add Alternative
        </button>
      </div>
      {(edited.alternatives_considered || []).map((alt, idx) => (
        <div key={idx} className="p-3 bg-white/5 rounded-xl border border-white/10 space-y-2">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={alt.name || ''}
              onChange={(e) => updateAltField(idx, 'name', e.target.value)}
              placeholder="Alternative name"
              className="input-field text-sm flex-1 py-2"
            />
            <button
              onClick={() => removeAlternative(idx)}
              className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
          <input
            type="text"
            value={alt.rejected_reason || ''}
            onChange={(e) => updateAltField(idx, 'rejected_reason', e.target.value)}
            placeholder="Reason rejected"
            className="input-field text-sm py-2"
          />
        </div>
      ))}
    </div>
  )

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary-400" />
          Edit Reasoning Record
        </h3>
        <div className="flex items-center gap-2">
          <button onClick={onCancel} className="btn-secondary text-sm px-4 py-2 flex items-center gap-1">
            <X className="w-4 h-4" /> Cancel
          </button>
          <button onClick={() => onSave(edited)} className="btn-primary text-sm px-4 py-2 flex items-center gap-1">
            <Save className="w-4 h-4" /> Save Changes
          </button>
        </div>
      </div>

      <div className="glass-card p-6 space-y-5">
        {renderStringField('what_changed', 'What Changed')}
        {renderStringField('business_objective', 'Business Objective')}
        {renderStringField('technical_objective', 'Technical Objective')}
        {renderAlternatives()}
        {renderListField('risks_accepted', 'Risks Accepted')}
        {renderListField('assumptions', 'Assumptions')}
        {renderStringField('timeline', 'Timeline')}
        {renderStringField('additional_context', 'Additional Context')}

        {/* Save/Cancel at bottom too */}
        <div className="flex items-center gap-3 pt-4 border-t border-white/10">
          <button onClick={() => onSave(edited)} className="btn-primary text-sm px-6 py-2.5 flex items-center gap-2">
            <Save className="w-4 h-4" /> Save Changes
          </button>
          <button onClick={onCancel} className="btn-secondary text-sm px-6 py-2.5 flex items-center gap-2">
            <X className="w-4 h-4" /> Cancel
          </button>
        </div>
      </div>
    </motion.div>
  )
}
