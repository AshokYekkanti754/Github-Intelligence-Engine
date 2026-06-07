// import React, { useState } from 'react';

// const ExportButton = ({ username, exportType = 'analysis', token }) => {
//   const [exporting, setExporting] = useState(false);
//   const [format, setFormat] = useState('json');
//   const [showMenu, setShowMenu] = useState(false);

//   const handleExport = async () => {
//     setExporting(true);
    
//     try {
//       let url = '';
//       switch (exportType) {
//         case 'analysis':
//           url = `http://localhost:8000/api/export/analysis/${username}?format=${format}`;
//           break;
//         case 'history':
//           url = `http://localhost:8000/api/export/my-history?format=${format}`;
//           break;
//         case 'saved':
//           url = `http://localhost:8000/api/export/saved-profiles?format=${format}`;
//           break;
//         case 'trend':
//           url = `http://localhost:8000/api/export/portfolio-trend/${username}?days=90&format=${format}`;
//           break;
//         default:
//           return;
//       }
      
//       const response = await fetch(url, {
//         headers: token ? { 'Authorization': `Bearer ${token}` } : {}
//       });
      
//       if (!response.ok) throw new Error('Export failed');
      
//       // Download file
//       const blob = await response.blob();
//       const downloadUrl = window.URL.createObjectURL(blob);
//       const a = document.createElement('a');
//       a.href = downloadUrl;
      
//       // Get filename from Content-Disposition header or create one
//       const contentDisposition = response.headers.get('Content-Disposition');
//       let filename = `export.${format}`;
//       if (contentDisposition) {
//         const match = contentDisposition.match(/filename="?(.+)"?/);
//         if (match) filename = match[1];
//       }
      
//       a.download = filename;
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       window.URL.revokeObjectURL(downloadUrl);
      
//     } catch (error) {
//       console.error('Export failed:', error);
//       alert('Failed to export data. Please try again.');
//     } finally {
//       setExporting(false);
//       setShowMenu(false);
//     }
//   };

//   return (
//     <div className="relative">
//       <button
//         onClick={() => setShowMenu(!showMenu)}
//         disabled={exporting}
//         className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition flex items-center gap-2"
//       >
//         <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//           <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
//         </svg>
//         {exporting ? 'Exporting...' : 'Export Data'}
//       </button>
      
//       {showMenu && (
//         <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-xl z-10 border border-gray-700">
//           <div className="p-2">
//             <div className="text-xs text-gray-400 px-3 py-1">Format</div>
//             <button
//               onClick={() => setFormat('json')}
//               className={`w-full text-left px-3 py-2 rounded-md text-sm ${format === 'json' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
//             >
//               JSON (.json)
//             </button>
//             <button
//               onClick={() => setFormat('csv')}
//               className={`w-full text-left px-3 py-2 rounded-md text-sm ${format === 'csv' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
//             >
//               CSV (.csv) - Excel compatible
//             </button>
//             <div className="border-t border-gray-700 my-2"></div>
//             <button
//               onClick={handleExport}
//               className="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded-md text-sm"
//             >
//               Download Now
//             </button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default ExportButton;