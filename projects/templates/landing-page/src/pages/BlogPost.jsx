import { useParams, Link } from 'react-router-dom';

export default function BlogPost() {
  const { slug } = useParams();
  
  return (
    <div className="max-w-2xl mx-auto py-10">
      <Link to="/blog" className="text-primary hover:underline mb-8 display-block">&larr; Back to Blog</Link>
      <h1 className="text-4xl font-bold mb-4 capitalize">{slug.replace('-', ' ')}</h1>
      <div className="prose prose-invert max-w-none">
        <p>This is a placeholder for the blog post content. In a real implementation, this would be loaded from a markdown file sourced from <code>data/blog/{slug}.md</code>.</p>
        <p>Agentic workflows allow for rapid iteration and deployment...</p>
      </div>
    </div>
  );
}
