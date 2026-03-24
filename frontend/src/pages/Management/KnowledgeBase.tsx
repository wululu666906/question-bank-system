import React from 'react';
import { Upload, FolderPlus, FileText } from 'lucide-react';

const KnowledgeBase: React.FC = () => {
  return (
    <div className="card animate-fade-in" style={{ height: '100%' }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.25rem' }}>知识库管理</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>上传原始学习资料或文档，提取核心知识点</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn-secondary"><FolderPlus size={18} /> 新建分类</button>
          <button className="btn-primary"><Upload size={18} /> 上传文档 (PDF/Word)</button>
        </div>
      </div>
      
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <FileText size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
        <h3>暂无知识库文献</h3>
        <p style={{ marginTop: '0.5rem' }}>点击右上角上传您的第一份学习资料</p>
      </div>
    </div>
  );
};

export default KnowledgeBase;
