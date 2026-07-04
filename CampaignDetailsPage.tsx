import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput, Pagination } from '../components/UI';
import { campaignService } from '../services';
import { Search, Plus, Filter } from 'lucide-react';

const CampaignDetailsPage: React.FC = () => {
  const [campaign, setCampaign] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [milestones, setMilestones] = React.useState<any[]>([]);
  const [updates, setUpdates] = React.useState<any[]>([]);
  const [comments, setComments] = React.useState<any[]>([]);
  const [newComment, setNewComment] = React.useState('');

  React.useEffect(() => {
    // Get campaign ID from URL params
    const campaignId = new URLSearchParams(window.location.search).get('id');
    if (campaignId) {
      fetchCampaignDetails(campaignId);
    }
  }, []);

  const fetchCampaignDetails = async (campaignId: string) => {
    try {
      const [campaignRes, milestonesRes, updatesRes, commentsRes] = await Promise.all([
        campaignService.getCampaign(campaignId),
        campaignService.getMilestones(campaignId),
        campaignService.getCampaignUpdates(campaignId),
        campaignService.getComments(campaignId),
      ]);

      setCampaign(campaignRes.data);
      setMilestones(milestonesRes.data || []);
      setUpdates(updatesRes.data || []);
      setComments(commentsRes.data || []);
    } catch (error) {
      console.error('Error fetching campaign details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!campaign || !newComment.trim()) return;

    try {
      await campaignService.addComment(campaign.id, {
        content: newComment,
        user_id: 'current-user-id',
      });
      setNewComment('');
      // Refresh comments
      const res = await campaignService.getComments(campaign.id);
      setComments(res.data || []);
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 p-8">Loading...</div>;
  }

  if (!campaign) {
    return <div className="min-h-screen bg-gray-50 p-8">Campaign not found</div>;
  }

  const progress = (campaign.raised_amount / campaign.target_amount) * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Campaign Header */}
        <Card className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <h1 className="text-3xl font-bold mb-2">{campaign.title}</h1>
              <p className="text-gray-600 mb-4">{campaign.description}</p>
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Progress</span>
                  <span className="font-semibold">{progress.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Goal</p>
              <p className="text-2xl font-bold">${campaign.target_amount.toLocaleString()}</p>
              <p className="text-sm text-gray-600 mt-2">Raised</p>
              <p className="text-2xl font-bold text-green-600">${campaign.raised_amount.toLocaleString()}</p>
              <Button variant="primary" className="w-full mt-4">Donate Now</Button>
            </div>
          </div>
        </Card>

        {/* Milestones */}
        {milestones.length > 0 && (
          <Card className="mb-8">
            <h2 className="text-xl font-bold mb-4">Milestones</h2>
            <div className="space-y-3">
              {milestones.map((milestone) => (
                <div key={milestone.id} className="border-l-4 border-blue-600 pl-4">
                  <h3 className="font-semibold">{milestone.title}</h3>
                  <p className="text-sm text-gray-600">${milestone.target_amount.toLocaleString()}</p>
                  <p className="text-sm text-gray-600">
                    {milestone.is_achieved ? '✓ Achieved' : 'In Progress'}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Updates */}
        {updates.length > 0 && (
          <Card className="mb-8">
            <h2 className="text-xl font-bold mb-4">Campaign Updates</h2>
            <div className="space-y-4">
              {updates.map((update) => (
                <div key={update.id} className="border-b pb-4">
                  <h3 className="font-semibold">{update.title}</h3>
                  <p className="text-gray-600 text-sm">{update.content}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    {new Date(update.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Comments Section */}
        <Card>
          <h2 className="text-xl font-bold mb-4">Comments ({comments.length})</h2>
          
          <div className="mb-6">
            <textarea
              className="w-full border border-gray-300 rounded-lg p-3 mb-2"
              rows={3}
              placeholder="Add a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
            <Button variant="primary" onClick={handleAddComment}>Post Comment</Button>
          </div>

          <div className="space-y-4">
            {comments.map((comment) => (
              <div key={comment.id} className="border rounded-lg p-3">
                <p className="font-semibold">{comment.user_id}</p>
                <p className="text-gray-600 text-sm mt-1">{comment.content}</p>
                <p className="text-xs text-gray-400 mt-2">
                  {new Date(comment.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default CampaignDetailsPage;
