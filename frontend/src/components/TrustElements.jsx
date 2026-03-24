import React from 'react';
import { ShieldCheck, Award, Star } from 'lucide-react';
import { motion } from 'framer-motion';
import { CMS_COPY } from '../lib/cms';

export const Testimonials = () => {
  return (
    <div className="py-24 grid grid-cols-1 lg:grid-cols-3 gap-8">
      {CMS_COPY.testimonials.map((t, i) => (
        <motion.div 
          key={i} 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.1 }}
          className="p-10 border-2 border-white/5 rounded-[2.5rem] bg-[#050505] hover:border-primary/20 transition-all duration-500 group"
        >
          <div className="flex gap-1 mb-6 text-primary/40 group-hover:text-primary transition-colors duration-500">
            {[1,2,3,4,5].map(s => <Star key={s} size={14} fill="currentColor" />)}
          </div>
          <p className="text-gray-400 italic mb-10 leading-relaxed text-sm">"{t.text}"</p>
          <div>
            <div className="text-xs font-black text-white uppercase tracking-widest mb-1">{t.name}</div>
            <div className="text-[10px] font-bold text-primary/60 uppercase tracking-widest">{t.role}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export const TrustBadges = () => (
  <div className="flex flex-wrap justify-center gap-12 py-16 opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-700">
    <div className="flex items-center gap-3 text-white font-black text-[10px] tracking-[0.3em] uppercase">
      <ShieldCheck className="text-primary" size={18} /> {CMS_COPY.trust_labels.secure}
    </div>
    <div className="flex items-center gap-3 text-white font-black text-[10px] tracking-[0.3em] uppercase">
      <Award className="text-primary" size={18} /> {CMS_COPY.trust_labels.rated}
    </div>
    <div className="flex items-center gap-3 text-white font-black text-[10px] tracking-[0.3em] uppercase">
      <Star className="text-primary" size={18} /> {CMS_COPY.trust_labels.support}
    </div>
  </div>
);
