import { useState, useEffect } from 'react';

// Mock loading from JSON via import or API
const affiliatesData = [
  {
    "name": "DigitalOcean",
    "description": "Simple, scalable cloud computing.",
    "category": "Hosting",
    "url": "#",
    "badges": ["Recommended"]
  },
  {
    "name": "PostHog",
    "description": "Product analytics suite.",
    "category": "Analytics",
    "url": "#",
    "badges": ["Stack Fit"]
  }
];

export default function Affiliates() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Trusted Tools</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {affiliatesData.map((item, i) => (
            <div key={i} className="bg-card-bg p-6 rounded-lg border border-gray-800 hover:border-primary transition-colors">
                <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-bold">{item.name}</h3>
                    <span className="bg-primary/20 text-primary text-xs px-2 py-1 rounded">{item.category}</span>
                </div>
                <p className="text-gray-400 mb-6">{item.description}</p>
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="block w-full text-center bg-gray-800 hover:bg-primary hover:text-black py-2 rounded font-bold transition-colors">
                    View Deal
                </a>
            </div>
        ))}
      </div>
    </div>
  );
}
