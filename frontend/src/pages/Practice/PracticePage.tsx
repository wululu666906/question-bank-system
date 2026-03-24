import React from 'react';
import { PenTool, PlayCircle } from 'lucide-react';

const PracticePage: React.FC = () => {
  return (
    <div className="card animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ padding: '2rem', textAlign: 'center', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ 
          width: '64px', height: '64px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', 
          color: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 1.5rem'
        }}>
          <PenTool size={32} />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>实战刷题模拟</h2>
        <p style={{ color: 'var(--text-secondary)' }}>检验学习成果，发现知识盲区</p>
      </div>
      
      <div style={{ padding: '2rem' }}>
        <div className="form-group">
          <label className="form-label" style={{ marginBottom: '1rem', display: 'block' }}>选择练习的知识范围</label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{ border: '1px solid var(--primary-color)', borderRadius: 'var(--radius-md)', padding: '1rem', backgroundColor: 'var(--primary-light)', cursor: 'pointer' }}>
              <div style={{ fontWeight: 600, color: 'var(--primary-color)', marginBottom: '0.25rem' }}>按知识点专项练习</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>选择特定知识模块进行针对性强化</div>
            </div>
            <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '1rem', cursor: 'pointer' }}>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>综合模拟考核</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>依据指定难度和题量自动组卷</div>
            </div>
          </div>
        </div>
        
        <button className="btn-primary w-full" style={{ padding: '1rem', fontSize: '1.1rem' }}>
          <PlayCircle size={20} /> 开始测试
        </button>
      </div>
    </div>
  );
};

export default PracticePage;
