import { Link } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { MessageSquare, Dumbbell, UtensilsCrossed, Target } from "lucide-react";

const quickActions = [
  {
    to: "/chat",
    icon: MessageSquare,
    title: "AI Chat",
    description: "Ask anything about fitness, diet, or workout plans",
    color: "bg-blue-500",
  },
  {
    to: "/workout",
    icon: Dumbbell,
    title: "Workout Plan",
    description: "Generate a personalized workout routine",
    color: "bg-orange-500",
  },
  {
    to: "/diet",
    icon: UtensilsCrossed,
    title: "Diet Plan",
    description: "Get a custom meal plan for your goals",
    color: "bg-green-500",
  },
  {
    to: "/profile",
    icon: Target,
    title: "Set Goals",
    description: "Update your fitness goals and preferences",
    color: "bg-purple-500",
  },
];

const examplePrompts = [
  "I want to bulk up with home workouts, give me a 5-day plan",
  "Create a vegetarian shredding diet with 2000 calories",
  "I'm a beginner, design a full body gym routine for weight loss",
  "Give me a non-veg muscle building diet plan with 4 meals a day",
  "I want to lean out, what exercises should I do at home?",
];

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.full_name?.split(" ")[0]}!
        </h1>
        <p className="text-gray-500 mt-2">
          What would you like to work on today?
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {quickActions.map(({ to, icon: Icon, title, description, color }) => (
          <Link
            key={to}
            to={to}
            className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow border"
          >
            <div
              className={`${color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}
            >
              <Icon size={24} className="text-white" />
            </div>
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          </Link>
        ))}
      </div>

      {/* Example Prompts */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Try asking the AI...
        </h2>
        <div className="space-y-2">
          {examplePrompts.map((prompt) => (
            <Link
              key={prompt}
              to={`/chat?prompt=${encodeURIComponent(prompt)}`}
              className="block p-3 bg-gray-50 rounded-lg hover:bg-primary-50 hover:text-primary-700 transition-colors text-sm text-gray-700"
            >
              "{prompt}"
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
