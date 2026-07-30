import { ExternalLink, FileText } from "lucide-react";
import { motion } from "framer-motion";

export default function Footer() {
  return (
    <footer className="py-16 px-4 border-t-2 border-[#F1F1F1]/10">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <div className="flex flex-col items-center sm:items-start gap-1">
            <span className="text-xl font-black text-[#F1F1F1] tracking-tight">LLM</span>
            <span className="text-sm font-medium text-[#F1F1F1]/40">
              Built for learning, experimentation, and curiosity.
            </span>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="#"
              className="p-2.5 border-2 border-[#F1F1F1]/10 text-[#F1F1F1]/40 hover:border-[#FF5722] hover:text-[#FF5722] transition-colors duration-150"
              aria-label="GitHub"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="p-2.5 border-2 border-[#F1F1F1]/10 text-[#F1F1F1]/40 hover:border-[#FF5722] hover:text-[#FF5722] transition-colors duration-150"
              aria-label="Documentation"
            >
              <FileText className="w-5 h-5" />
            </a>
          </div>
        </motion.div>

        <div className="mt-8 pt-8 border-t-2 border-[#F1F1F1]/5 text-center">
          <p className="text-xs font-bold text-[#F1F1F1]/30 uppercase tracking-wider">
            An open-source research and learning project. Not a commercial product.
          </p>
        </div>
      </div>
    </footer>
  );
}
