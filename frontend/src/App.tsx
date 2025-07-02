import { useEffect, useState, useRef } from 'react';
import './App.css';
import {
  getSubmissions,
  createSubmission,
  updateSubmission,
  deleteSubmission,
} from './api';
import type { Submission, PaginatedSubmissions } from './api';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const contactOptions = ['Email', 'Phone', 'Both'] as const;
const contactOptionsWithEmpty = ['Email', 'Phone', 'Both', ''] as const;

const submissionSchema = z.object({
  full_name: z.string().min(1, 'Full Name is required'),
  email: z.string().email('Invalid email'),
  phone_number: z.string().min(7, 'Phone Number must be 7-20 digits').max(20, 'Phone Number must be 7-20 digits').regex(/^[\d]{7,20}$/, 'Phone Number must be 7-20 digits'),
  age: z.coerce.number().min(18, 'Age must be between 18 and 120').max(120, 'Age must be between 18 and 120'),
  address: z.string().optional(),
  preferred_contact: z.enum(contactOptionsWithEmpty, { errorMap: () => ({ message: 'Select a contact method' }) }),
});

type SubmissionForm = z.infer<typeof submissionSchema>;

const initialForm: SubmissionForm = {
  full_name: '',
  email: '',
  phone_number: '',
  age: '' as unknown as number,
  address: '',
  preferred_contact: '',
};

function App() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const toastTimeout = useRef<NodeJS.Timeout | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SubmissionForm>({
    resolver: zodResolver(submissionSchema),
    defaultValues: initialForm,
  });
  const [loading, setLoading] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null);

  // Debounce effect for search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  useEffect(() => {
    setPage(1); // Reset to first page on search
  }, [debouncedSearch]);

  const fetchData = async () => {
    try {
      const params: Record<string, any> = {
        skip: (page - 1) * limit,
        limit,
      };
      if (debouncedSearch) params.search = debouncedSearch;
      const data: PaginatedSubmissions = await getSubmissions(params);
      setSubmissions(data.items);
      setTotal(data.total);
    } catch (e: any) {
      setError('Failed to fetch submissions');
      showToast('error', 'Failed to fetch submissions. Please try again later.');
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, page, limit]);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    if (toastTimeout.current) clearTimeout(toastTimeout.current);
    toastTimeout.current = setTimeout(() => setToast(null), 3000);
  };

  const onSubmit = async (data: SubmissionForm) => {
    setError(null);
    setLoading(true);
    try {
      let response;
      const submissionData = data as unknown as import('./api').SubmissionInput;
      if (editingId) {
        response = await updateSubmission(editingId, submissionData);
        setMessage('Submission updated successfully');
        showToast('success', 'Submission updated successfully');
      } else {
        response = await createSubmission(submissionData);
        if (response && response.id) {
          setMessage('Create A Form Submission');
          showToast('success', 'Create A Form Submission');
        } else {
          setMessage('Form Not Submitted');
          showToast('error', 'Form Not Submitted');
        }
      }
      reset(initialForm);
      setEditingId(null);
      fetchData();
    } catch (e: any) {
      let apiMsg = 'Form Not Submitted';
      if (e.response?.data?.detail) {
        apiMsg = e.response.data.detail;
      } else if (e.message && e.message.includes('Network')) {
        apiMsg = 'Network error. Please check your connection.';
      } else if (e.response?.status >= 500) {
        apiMsg = 'Server error. Please try again later.';
      }
      setError(apiMsg);
      showToast('error', apiMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (sub: Submission) => {
    reset({ ...sub });
    setEditingId(sub.id);
    setError(null);
    setMessage(null);
  };

  const handleDelete = async (id: number) => {
    setPendingDeleteId(id);
  };

  const confirmDelete = async () => {
    if (pendingDeleteId === null) return;
    setLoading(true);
    try {
      await deleteSubmission(pendingDeleteId);
      setMessage('Submission deleted successfully');
      showToast('success', 'Submission deleted successfully');
      fetchData();
    } catch (e: any) {
      let apiMsg = 'Error deleting submission';
      if (e.response?.data?.detail) {
        apiMsg = e.response.data.detail;
      } else if (e.message && e.message.includes('Network')) {
        apiMsg = 'Network error. Please check your connection.';
      } else if (e.response?.status >= 500) {
        apiMsg = 'Server error. Please try again later.';
      }
      setError(apiMsg);
      showToast('error', apiMsg);
    } finally {
      setLoading(false);
      setPendingDeleteId(null);
    }
  };

  const cancelDelete = () => {
    setPendingDeleteId(null);
  };

  return (
    <>
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed z-50 top-4 left-1/2 -translate-x-1/2 sm:left-auto sm:right-6 sm:translate-x-0 transition-all duration-300 ${toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white px-6 py-3 rounded shadow-lg flex items-center gap-2`}>
          {toast.type === 'success' ? (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
          ) : (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          )}
          <span className="font-medium">{toast.message}</span>
        </div>
      )}
      <div className="min-h-screen w-full bg-red-500 bg-gradient-to-br from-blue-50 to-blue-100">
        {/* Delete Confirmation Modal */}
        {pendingDeleteId !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-10 px-2">
            <div className="bg-white rounded-lg shadow-xl p-4 sm:p-8 w-full max-w-xs sm:max-w-sm md:max-w-md text-center">
              <h3 className="text-lg font-semibold mb-4">Confirm Deletion</h3>
              <p className="mb-6 text-gray-700">Are you sure you want to delete this submission?</p>
              <div className="flex flex-col sm:flex-row justify-center gap-2 sm:gap-4">
                <button
                  onClick={cancelDelete}
                  className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 w-full sm:w-auto"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDelete}
                  className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-60 w-full sm:w-auto"
                  disabled={loading}
                >
                  {loading ? (
                    <svg className="animate-spin h-5 w-5 mr-2 inline-block text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
                  ) : null}
                  Yes, Delete
                </button>
              </div>
            </div>
          </div>
        )}
        <div className="max-w-7xl mx-auto flex-1 flex flex-col py-4 px-1 sm:py-6 sm:px-2 lg:px-8">
          <div className="text-center mb-6 sm:mb-10">
            <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
              <span className="text-green-500 text-center block">Form Management System</span>
            </h1>
            <p className="mt-2 sm:mt-3 max-w-2xl mx-auto text-base sm:text-xl text-gray-600">
              Manage your form submissions efficiently
            </p>
          </div>

          <div className="flex flex-col gap-8 md:gap-16">
            {/* Form Section */}
            <div className="bg-white rounded-xl shadow-xl overflow-hidden w-full max-w-xs sm:max-w-lg md:max-w-2xl mx-auto mb-8 p-3 sm:p-6 md:p-8">
              <form onSubmit={handleSubmit(onSubmit)}>
                <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-6 sm:mb-8 text-center">Submit Your Details</h2>
                <div className="space-y-4 sm:space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="full_name" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Full Name<span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('full_name')}
                      id="full_name"
                      name="full_name"
                      type="text"
                      placeholder="John Doe"
                      className="mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base"
                    />
                  </div>
                  {errors.full_name && (
                    <p className="mt-1 text-sm text-red-400 sm:ml-40">{errors.full_name.message}</p>
                  )}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="address" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Address
                    </label>
                    <textarea
                      {...register('address')}
                      id="address"
                      name="address"
                      rows={2}
                      className="mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base"
                      placeholder="123 Main St, City"
                    />
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="email" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Email<span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('email')}
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      placeholder="john@example.com"
                      className="mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-400 sm:ml-40">{errors.email.message}</p>
                  )}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="phone_number" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Phone Number<span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('phone_number')}
                      id="phone_number"
                      name="phone_number"
                      type="text"
                      placeholder="1234567890"
                      className="mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base"
                    />
                  </div>
                  {errors.phone_number && (
                    <p className="mt-1 text-sm text-red-400 sm:ml-40">{errors.phone_number.message}</p>
                  )}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="age" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Age<span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('age', { valueAsNumber: true })}
                      id="age"
                      name="age"
                      type="number"
                      min={18}
                      max={120}
                      placeholder="25"
                      className="mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base"
                    />
                  </div>
                  {errors.age && (
                    <p className="mt-1 text-sm text-red-400 sm:ml-40">{errors.age.message}</p>
                  )}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:gap-6">
                    <label htmlFor="preferred_contact" className="sm:w-40 block text-sm font-medium text-gray-900 mb-1 sm:mb-0">
                      Preferred Contact Method<span className="text-red-500">*</span>
                    </label>
                    <select
                      {...register('preferred_contact')}
                      id="preferred_contact"
                      name="preferred_contact"
                      className={`mt-1 sm:mt-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 text-sm sm:text-base ${errors.preferred_contact ? 'border-red-500' : ''}`}
                    >
                      <option value="">Select...</option>
                      {contactOptions.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  </div>
                  {errors.preferred_contact && (
                    <p className="mt-1 text-sm text-red-400 sm:ml-40">{errors.preferred_contact.message}</p>
                  )}
                </div>
                {/* Actions */}
                <div className="mt-4 sm:mt-6 flex flex-col sm:flex-row items-center justify-end gap-x-0 gap-y-2 sm:gap-x-6 sm:gap-y-0">
                  {editingId && (
                    <button
                      type="button"
                      className="text-sm font-semibold text-gray-900"
                      onClick={() => { reset(initialForm); setEditingId(null); }}
                    >
                      Cancel
                    </button>
                  )}
                  <button
                    type="submit"
                    className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-60 disabled:cursor-not-allowed w-full sm:w-auto"
                    disabled={loading}
                  >
                    {loading ? (
                      <svg className="animate-spin h-5 w-5 mr-2 inline-block text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
                    ) : null}
                    {editingId ? 'Update Submission' : 'Create Submission'}
                  </button>
                </div>
                {error && (
                  <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-red-100 border-l-4 border-red-500 text-red-700 text-sm sm:text-base">
                    <p>{error}</p>
                  </div>
                )}
                {message && (
                  <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-green-100 border-l-4 border-green-500 text-green-700 text-sm sm:text-base">
                    <p>{message}</p>
                  </div>
                )}
              </form>
            </div>

            {/* Submissions Table Section */}
            <div className="bg-white rounded-xl shadow-xl overflow-x-auto w-full max-w-xs sm:max-w-2xl md:max-w-4xl mx-auto p-2 sm:p-6 md:p-8">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-6 sm:mb-8 text-center">Submissions</h2>
              <div className="mb-4 sm:mb-6">
                <input
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  placeholder="Search by name or email..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              {/* Pagination Controls */}
              <div className="flex flex-col sm:flex-row items-center justify-between mb-2 sm:mb-4 gap-2 sm:gap-0">
                <div className="flex gap-2">
                  <button
                    className="px-2 sm:px-3 py-1 rounded bg-gray-200 text-gray-700 mr-1 sm:mr-2 disabled:opacity-50 text-xs sm:text-sm"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </button>
                  <button
                    className="px-2 sm:px-3 py-1 rounded bg-gray-200 text-gray-700 disabled:opacity-50 text-xs sm:text-sm"
                    onClick={() => setPage(p => (p * limit < total ? p + 1 : p))}
                    disabled={page * limit >= total}
                  >
                    Next
                  </button>
                </div>
                <div className="text-gray-600 text-xs sm:text-sm">
                  Page {page} of {Math.max(1, Math.ceil(total / limit))} | Total: {total}
                </div>
                <div>
                  <label className="mr-1 sm:mr-2 text-gray-600 text-xs sm:text-sm">Per page:</label>
                  <select
                    className="border rounded px-1 sm:px-2 py-1 text-xs sm:text-sm"
                    value={limit}
                    onChange={e => { setLimit(Number(e.target.value)); setPage(1); }}
                  >
                    {[5, 10, 20, 50].map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-xs sm:text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">ID</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Name</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Email</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Phone</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Age</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Contact</th>
                      <th scope="col" className="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {submissions.map(sub => (
                      <tr key={sub.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap text-gray-700">{sub.id}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap font-medium text-gray-900">{sub.full_name}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap text-gray-700">{sub.email}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap text-gray-700">{sub.phone_number}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap text-gray-700">{sub.age}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap text-gray-700">{sub.preferred_contact}</td>
                        <td className="px-2 sm:px-4 py-2 sm:py-4 whitespace-nowrap font-medium">
                          <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-2">
                            <button
                              onClick={() => handleEdit(sub)}
                              className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-2 sm:px-3 py-1 rounded-md transition-colors text-xs sm:text-sm"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDelete(sub.id)}
                              className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-2 sm:px-3 py-1 rounded-md transition-colors text-xs sm:text-sm"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {submissions.length === 0 && (
                  <div className="text-center py-6 sm:py-8 text-gray-500 text-sm sm:text-base">
                    No submissions found
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;