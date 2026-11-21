#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include <cmath>
#include <vector>

class LidarAngleFilterNode : public rclcpp::Node
{
public:
  LidarAngleFilterNode()
  : Node("lidar_angle_filter")
  {
    // Declare parameters with default values
    this->declare_parameter<std::string>("scan_topic", "scan");
    this->declare_parameter<double>("min_angle_deg", -150.0);
    this->declare_parameter<double>("max_angle_deg", 150.0);

    // Get parameter values
    scan_topic_ = this->get_parameter("scan_topic").as_string();
    min_angle_deg_ = this->get_parameter("min_angle_deg").as_double();
    max_angle_deg_ = this->get_parameter("max_angle_deg").as_double();

    // Setup subscriber and publisher
    scan_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      scan_topic_, 10,
      std::bind(&LidarAngleFilterNode::scanCallback, this, std::placeholders::_1)
    );

    filtered_scan_pub_ = this->create_publisher<sensor_msgs::msg::LaserScan>("filtered_scan", 10);

    RCLCPP_INFO(this->get_logger(), "lidar_angle_filter node started with range [%.1f, %.1f] degrees",
                min_angle_deg_, max_angle_deg_);
  }

private:
  void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
  {
    auto filtered_msg = *msg; // Copy the full message first
    auto& ranges = filtered_msg.ranges;

    double angle_min_deg = radiansToDegrees(msg->angle_min);
    double angle_increment_deg = radiansToDegrees(msg->angle_increment);

    for (size_t i = 0; i < ranges.size(); ++i) {
      double angle_deg = angle_min_deg + i * angle_increment_deg;

      // Normalize angle to [-180, 180]
      angle_deg = normalizeAngle(angle_deg);

      // Invalidate readings outside the desired range
      if (angle_deg < min_angle_deg_ || angle_deg > max_angle_deg_) {
        ranges[i] = std::numeric_limits<float>::quiet_NaN();
      }
    }

    filtered_scan_pub_->publish(filtered_msg);
  }

  double radiansToDegrees(double radians)
  {
    return radians * 180.0 / M_PI;
  }

  double normalizeAngle(double angle_deg)
  {
    while (angle_deg > 180.0) angle_deg -= 360.0;
    while (angle_deg < -180.0) angle_deg += 360.0;
    return angle_deg;
  }

  // Node parameters
  double min_angle_deg_;
  double max_angle_deg_;
  std::string scan_topic_;

  // ROS interfaces
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr filtered_scan_pub_;
};

int main(int argc, char* argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<LidarAngleFilterNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}