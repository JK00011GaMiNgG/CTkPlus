#include <vector>
#include <cmath>
#include <utility>

using namespace std;

class Shape {
    public:
        virtual pair<int, int> get_points(int index) const = 0;
        virtual int get_vertex_amount() const = 0;
};

class VertexShape : public Shape {
    public:
        void init(vector<int> vertices, bool snap) {
            this->snap = snap;
            this->vertices = format(vertices);
        }

        int get_vertex_amount() const override {
            return this->vertices.size();
        }

        pair<int, int> get_points(int index) const override {
            return this->vertices[index];
        }

    private:
        vector<pair<int, int>> vertices;
        bool snap;

        vector<pair<int, int>> format(vector<int> vertices) {
            vector<pair<int, int>> points;
            int n = 0;
            int m = 1;

            for (int i = 0; i < vertices.size() / 2; i++) {
                int x = vertices[m];
                int y = vertices[n];
                points.push_back(make_pair(x, y));
                m += 2;
                n += 2;
            }

            if (snap) {
                int x = vertices[0];
                int y = vertices[1];
                points.push_back(make_pair(x, y));
            }

            return points;
        }
};

class EllipseShape : public Shape {
    public:
        void init(int width, int height, int num_points = 100, bool snap = true) {
            this->width = width;
            this->height = height;
            this->snap = snap;
            this->vertices = generate_vertices(width, height, num_points);
        }

        int get_vertex_amount() const override {
            return this->vertices.size();
        }

        pair<int, int> get_points(int index) const override {
            return this->vertices[index];
        }

    private:
        vector<pair<int, int>> vertices;
        bool snap;
        int width, height;

        vector<pair<int, int>> generate_vertices(int width, int height, int num_points) {
            vector<pair<int, int>> points;
            double a = width / 2.0;
            double b = height / 2.0;

            for (int i = 0; i < num_points; i++) {
                double t = (2 * M_PI * i) / num_points;
                int x = static_cast<int>(a * cos(t));
                int y = static_cast<int>(b * sin(t));
                points.push_back(make_pair(x, y));
            }

            if (snap) {
                points.push_back(points[0]);
            }

            return points;
        }
};