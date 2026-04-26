import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Dumbbell, Loader2 } from "lucide-react";
import { generateWorkoutPlan } from "../api/client";

export default function WorkoutPlan() {
  const [goal, setGoal] = useState("bulking");
  const [location, setLocation] = useState("gym");
  const [experience, setExperience] = useState("beginner");
  const [days, setDays] = useState(5);
  const [duration, setDuration] = useState(60);
  const [requirements, setRequirements] = useState("");
  const [plan, setPlan] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setPlan(null);
    try {
      const res = await generateWorkoutPlan({
        goal,
        location,
        experience_level: experience,
        days_per_week: days,
        duration_minutes: duration,
        specific_requirements: requirements || undefined,
      });
      setPlan(res.data.content);
    } catch {
      setPlan("Failed to generate plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
          <Dumbbell className="text-orange-600" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workout Plan Generator</h1>
          <p className="text-gray-500">Get a personalized workout routine from AI</p>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Goal</label>
            <select value={goal} onChange={(e) => setGoal(e.target.value)} className="w-full px-3 py-2 border rounded-lg">
              <option value="bulking">Bulking</option>
              <option value="shredding">Shredding</option>
              <option value="leaning">Leaning</option>
              <option value="general_fitness">General Fitness</option>
              <option value="weight_loss">Weight Loss</option>
              <option value="muscle_gain">Muscle Gain</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <select value={location} onChange={(e) => setLocation(e.target.value)} className="w-full px-3 py-2 border rounded-lg">
              <option value="gym">Gym</option>
              <option value="home">Home</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Experience Level</label>
            <select value={experience} onChange={(e) => setExperience(e.target.value)} className="w-full px-3 py-2 border rounded-lg">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Days per Week</label>
            <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg">
              {[3, 4, 5, 6].map((d) => (
                <option key={d} value={d}>{d} days</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Session Duration</label>
            <select value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg">
              {[30, 45, 60, 75, 90].map((d) => (
                <option key={d} value={d}>{d} minutes</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Special Requirements</label>
            <input
              type="text"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              placeholder="e.g. bad knees, no deadlifts"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-6 bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? <Loader2 size={20} className="animate-spin" /> : <Dumbbell size={20} />}
          {loading ? "Generating..." : "Generate Workout Plan"}
        </button>
      </div>

      {plan && (
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Your Workout Plan</h2>
          <div className="prose max-w-none">
            <ReactMarkdown>{plan}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
