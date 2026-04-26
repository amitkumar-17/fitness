import { useState, useEffect } from "react";
import { User } from "lucide-react";
import { getProfile, updateProfile } from "../api/client";
import { useAuthStore } from "../store/authStore";

export default function Profile() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const token = useAuthStore((s) => s.token);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    age: "",
    weight_kg: "",
    height_cm: "",
    fitness_goal: "",
    diet_preference: "",
    workout_location: "",
    experience_level: "",
  });

  useEffect(() => {
    getProfile()
      .then((res) => {
        const u = res.data;
        setForm({
          full_name: u.full_name || "",
          age: u.age?.toString() || "",
          weight_kg: u.weight_kg?.toString() || "",
          height_cm: u.height_cm?.toString() || "",
          fitness_goal: u.fitness_goal || "",
          diet_preference: u.diet_preference || "",
          workout_location: u.workout_location || "",
          experience_level: u.experience_level || "",
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSuccess(false);
    try {
      const data: Record<string, unknown> = { ...form };
      if (form.age) data.age = Number(form.age);
      if (form.weight_kg) data.weight_kg = Number(form.weight_kg);
      if (form.height_cm) data.height_cm = Number(form.height_cm);

      const res = await updateProfile(data);
      setAuth(token!, res.data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch {
      /* noop */
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-gray-500">Loading...</div>;

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
          <User className="text-purple-600" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>
          <p className="text-gray-500">
            Set your preferences so the AI can personalize your plans
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input type="text" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
            <input type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
            <input type="number" value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Height (cm)</label>
            <input type="number" value={form.height_cm} onChange={(e) => setForm({ ...form, height_cm: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Fitness Goal</label>
          <select value={form.fitness_goal} onChange={(e) => setForm({ ...form, fitness_goal: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
            <option value="">Select a goal</option>
            <option value="bulking">Bulking</option>
            <option value="shredding">Shredding</option>
            <option value="leaning">Leaning</option>
            <option value="general_fitness">General Fitness</option>
            <option value="weight_loss">Weight Loss</option>
            <option value="muscle_gain">Muscle Gain</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Diet Preference</label>
          <select value={form.diet_preference} onChange={(e) => setForm({ ...form, diet_preference: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
            <option value="">Select diet type</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="non_vegetarian">Non-Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="eggetarian">Eggetarian</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Workout Location</label>
          <select value={form.workout_location} onChange={(e) => setForm({ ...form, workout_location: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
            <option value="">Select location</option>
            <option value="home">Home</option>
            <option value="gym">Gym</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Experience Level</label>
          <select value={form.experience_level} onChange={(e) => setForm({ ...form, experience_level: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
            <option value="">Select level</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        {success && (
          <div className="bg-green-50 text-green-600 p-3 rounded-lg text-sm">
            Profile updated successfully!
          </div>
        )}

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Profile"}
        </button>
      </div>
    </div>
  );
}
