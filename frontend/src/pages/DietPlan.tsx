import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { UtensilsCrossed, Loader2 } from "lucide-react";
import { generateDietPlan } from "../api/client";

export default function DietPlan() {
  const [goal, setGoal] = useState("bulking");
  const [dietType, setDietType] = useState("non_vegetarian");
  const [meals, setMeals] = useState(4);
  const [calories, setCalories] = useState<number | "">("");
  const [allergies, setAllergies] = useState("");
  const [requirements, setRequirements] = useState("");
  const [plan, setPlan] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setPlan(null);
    try {
      const res = await generateDietPlan({
        goal,
        diet_type: dietType,
        meals_per_day: meals,
        calories_target: calories || undefined,
        allergies: allergies ? allergies.split(",").map((a) => a.trim()) : [],
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
        <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
          <UtensilsCrossed className="text-green-600" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Diet Plan Generator</h1>
          <p className="text-gray-500">Get a personalized meal plan from AI</p>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Diet Type</label>
            <select value={dietType} onChange={(e) => setDietType(e.target.value)} className="w-full px-3 py-2 border rounded-lg">
              <option value="vegetarian">Vegetarian</option>
              <option value="non_vegetarian">Non-Vegetarian</option>
              <option value="vegan">Vegan</option>
              <option value="eggetarian">Eggetarian</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Meals per Day</label>
            <select value={meals} onChange={(e) => setMeals(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg">
              {[3, 4, 5, 6].map((m) => (
                <option key={m} value={m}>{m} meals</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Calories (optional)</label>
            <input
              type="number"
              value={calories}
              onChange={(e) => setCalories(e.target.value ? Number(e.target.value) : "")}
              placeholder="e.g. 2500"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Allergies (comma-separated)</label>
            <input
              type="text"
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
              placeholder="e.g. nuts, shellfish, gluten"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Special Requirements</label>
            <input
              type="text"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              placeholder="e.g. lactose free, high fiber"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-6 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? <Loader2 size={20} className="animate-spin" /> : <UtensilsCrossed size={20} />}
          {loading ? "Generating..." : "Generate Diet Plan"}
        </button>
      </div>

      {plan && (
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Your Diet Plan</h2>
          <div className="prose max-w-none">
            <ReactMarkdown>{plan}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
